import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("GpuReservations")

def lambda_handler(event, context):
    try:
        print("🧪 Cancel Handler Event:", json.dumps(event))

        # クエリ or パスから reservation_id を取得
        body = json.loads(event.get("body", "{}"))
        reservation_id = body.get("reservation_id")
        if not reservation_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "reservation_id is required"})
            }

        # ① まず該当レコードを取得
        response = table.get_item(Key={"id": reservation_id})
        item = response.get("Item")

        if not item:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "予約が見つかりません"})
            }

        # ② 状態チェック
        if item.get("status") not in ["pending", "approved", "pending_conflict"]:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "この予約はキャンセルできません"})
            }


        # ③ ステータスを rejected に更新
        table.update_item(
            Key={"id": reservation_id},
            UpdateExpression="SET #s = :new_status",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":new_status": "rejected"}
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "予約をキャンセルしました", "id": reservation_id})
        }

    except Exception as e:
        print("❌ Cancel Reservation Error:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

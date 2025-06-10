import json
import boto3
from boto3.dynamodb.conditions import Key
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("GpuReservations")

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        reservation_id = body.get("reservation_id")
        decision = body.get("decision")  # ← "approve", "reject", "keep" を期待

        if not reservation_id or not decision:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "reservation_id and decision are required"})
            }

        # 予約の存在を確認
        response = table.get_item(Key={"id": reservation_id})
        if "Item" not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Reservation not found"})
            }

        # 新ステータスの決定
        if decision == "approve":
            new_status = "approved"
        elif decision == "reject":
            new_status = "rejected"
        elif decision == "keep":
            new_status = "pending"
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid decision value"})
            }

        # ステータスを更新
        table.update_item(
            Key={"id": reservation_id},
            UpdateExpression="SET #s = :s",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": new_status}
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Reservation {reservation_id} updated to {new_status}"
            })
        }

    except Exception as e:
        logger.error("❌ Error in confirm_reject_handler: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

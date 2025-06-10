import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("GpuReservations")

def lambda_handler(event, context):
    try:
        print("🧪 get_pending_conflicts イベント:", json.dumps(event))

        headers = event.get("headers", {})
        auth_header = headers.get("authorization") or headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Authorization header is missing or invalid"})
            }

        token = auth_header.replace("Bearer ", "")
        user_id = token.split("-")[0]

        response = table.query(
            IndexName="user_id-index",
            KeyConditionExpression=Key("user_id").eq(user_id)
        )

        items = response.get("Items", [])
        # pending_conflict だけ抽出
        conflicts = [item for item in items if item.get("status") == "pending_conflict"]

        return {
            "statusCode": 200,
            "body": json.dumps(conflicts, default=str)
        }

    except Exception as e:
        print("❌ get_pending_conflicts エラー:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

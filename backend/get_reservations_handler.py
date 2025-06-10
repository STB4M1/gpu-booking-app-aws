import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("GpuReservations")

def lambda_handler(event, context):
    try:
        headers = event.get("headers", {})
        auth_header = headers.get("authorization") or headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Authorization header is missing or invalid"})
            }

        token = auth_header.replace("Bearer ", "")
        user_id = token.split("-")[0]  # トークン形式が "userID-タイムスタンプ" の前提

        if not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "user_id could not be extracted from token"})
            }

        query = event.get("queryStringParameters") or {}
        status_filter = query.get("status") if query else None

        # user_id に基づいて予約取得
        response = table.query(
            IndexName="user_id-index",
            KeyConditionExpression=Key("user_id").eq(user_id)
        )

        items = response.get("Items", [])

        # status フィルタがあれば適用
        if status_filter:
            items = [item for item in items if item.get("status") == status_filter]

        return {
            "statusCode": 200,
            "body": json.dumps(items, default=str)
        }

    except Exception as e:
        print("❌ Error retrieving reservations:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

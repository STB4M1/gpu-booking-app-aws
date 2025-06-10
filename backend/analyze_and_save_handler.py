import json
import uuid
from datetime import datetime
from bedrock_client import analyze_text_with_bedrock
from schemas import ReservationCreate
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

# DynamoDB テーブル名（環境変数にしてもOK）
TABLE_NAME = "GpuReservations"
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # 自然文の抽出
        body = json.loads(event["body"])
        text = body.get("text", "")
        if not text:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "text is required."})
            }

        # 1. 自然文 → 構造化（Bedrock）
        structured = analyze_text_with_bedrock(text)

        # 2. 必須キーの確認
        required = {"start_time", "end_time", "purpose", "priority_score", "server_name"}
        missing_fields = [key for key in required if not structured.get(key)]

        if missing_fields:
            return {
                "statusCode": 422,
                "body": json.dumps({
                    "error": "構造化結果に必要な情報が不足しています。",
                    "missing_fields": missing_fields  # ← Flutterでここを使って表示できる
                })
            }

        headers = event.get("headers", {})
        auth_header = headers.get("authorization") or headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Authorization header is missing or invalid"})
            }
        user_id = auth_header.split(" ")[1].split("-")[0]
        print("🧾 user_id:", user_id)

        # 3. Pydanticバリデーション
        data = ReservationCreate(
            user_id=user_id,
            start_time=datetime.fromisoformat(structured["start_time"]),
            end_time=datetime.fromisoformat(structured["end_time"]),
            purpose=structured["purpose"],
            server_name=structured["server_name"],
            priority_score=structured["priority_score"],
            received_text=structured.get("received_text", text)
        )

        # 4. 競合チェック：同じサーバ・重なった時間帯の予約を取得
        response = table.scan(
            FilterExpression=(
                (Key("server_name").eq(data.server_name)) &
                (Attr("start_time").lt(data.end_time.isoformat())) &
                (Attr("end_time").gt(data.start_time.isoformat()))
            )
        )
        existing = response.get("Items", [])

        # 優先度の比較
        # 競合するすべての予約と比較
        conflicting_items = [
            item for item in existing
            if item["status"] in ("approved", "pending", "pending_conflict")
        ]

        if not conflicting_items:
            status = "approved"
        else:
            max_existing_score = max(float(item["priority_score"]) for item in conflicting_items)
            if float(data.priority_score) > max_existing_score:
                status = "approved"
            else:
                status = "pending_conflict"


        # 保存用データ構築
        item = {
            **data.dict(),
            "id": str(uuid.uuid4()),
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
            "start_time": data.start_time.isoformat(),
            "end_time": data.end_time.isoformat(),
            "priority_score": Decimal(str(data.priority_score))
        }
        print("🧾 登録するitem:", item)

        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "body": json.dumps(item, default=str)
        }

    except Exception as e:
        print("❌ Lambda Error:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

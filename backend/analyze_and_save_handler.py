import json
import uuid
from datetime import datetime
from bedrock_client import analyze_text_with_bedrock
from schemas import ReservationCreate
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

TABLE_NAME = "GpuReservations"
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        print("📥 Event received:", event)

        # 1. JSON読み込み
        body = json.loads(event["body"])
        text = body.get("text", "")
        if not text:
            return {"statusCode": 400, "body": json.dumps({"error": "text is required."})}
        print("📝 入力テキスト:", text)

        # 2. 自然文を構造化
        structured = analyze_text_with_bedrock(text)
        print("🧠 構造化結果:", structured)

        # 3. 必須フィールド確認
        required = {"start_time", "end_time", "purpose", "priority_score", "server_name"}
        missing_fields = [key for key in required if not structured.get(key)]
        if missing_fields:
            return {
                "statusCode": 422,
                "body": json.dumps({
                    "error": "構造化結果に必要な情報が不足しています。",
                    "missing_fields": missing_fields
                })
            }

        # 4. 認証チェック
        headers = event.get("headers", {})
        auth_header = headers.get("authorization") or headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Authorization header is missing or invalid"})
            }
        user_id = auth_header.split(" ")[1].split("-")[0]
        print("🔐 user_id:", user_id)

        # 5. バリデーション
        data = ReservationCreate(
            user_id=user_id,
            start_time=datetime.fromisoformat(structured["start_time"]),
            end_time=datetime.fromisoformat(structured["end_time"]),
            purpose=structured["purpose"],
            server_name=structured["server_name"],
            priority_score=structured["priority_score"],
            received_text=structured.get("received_text", text)
        )
        print("✅ バリデーション成功")

        # 6. reservation_id 構成（ユーザー、時間、サーバーで一意）
        reservation_id = f"{user_id}_{data.server_name}_{data.start_time.isoformat()}_{data.end_time.isoformat()}"
        print("🆔 reservation_id:", reservation_id)

        # 7. 重複チェック（同サーバー & 時間帯が重なる予約）
        response = table.scan(
            FilterExpression=(
                Attr("server_name").eq(data.server_name) &
                Attr("start_time").lt(data.end_time.isoformat()) &
                Attr("end_time").gt(data.start_time.isoformat())
            )
        )
        existing = response.get("Items", [])
        print(f"🔍 重複候補: {len(existing)}件")

        conflicting_items = [
            item for item in existing
            if item.get("status") in ("approved", "pending", "pending_conflict")
        ]
        print(f"⚠️ 競合予約: {len(conflicting_items)}件")

        # 8. 優先度比較とステータス決定
        if not conflicting_items:
            status = "approved"
        else:
            max_score = max(float(item["priority_score"]) for item in conflicting_items)
            status = "approved" if float(data.priority_score) > max_score else "pending_conflict"
        print("✅ ステータス判定:", status)

        # 9. 他の予約のステータスも調整（自分がapprovedなら他をpending_conflictへ）
        if status == "approved":
            for item in conflicting_items:
                if item["status"] == "approved":
                    print("⚠️ 他の予約を pending_conflict に更新:", item["id"])
                    table.update_item(
                        Key={"id": item["id"]},
                        UpdateExpression="SET #s = :s",
                        ExpressionAttributeNames={"#s": "status"},
                        ExpressionAttributeValues={":s": "pending_conflict"}
                    )

        # 10. 同一 reservation_id の予約を削除（あれば）
        try:
            existing_res = table.query(
                IndexName="reservation_id-index",
                KeyConditionExpression=Key("reservation_id").eq(reservation_id)
            )
            for old in existing_res.get("Items", []):
                print("🗑 旧予約削除:", old["id"])
                table.delete_item(Key={"id": old["id"]})
        except Exception as e:
            print("❌ reservation_id GSIまたは削除でエラー:", e)

        # 11. 新しい予約データ構築
        item = {
            **data.dict(),
            "id": str(uuid.uuid4()),
            "reservation_id": reservation_id,
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
            "start_time": data.start_time.isoformat(),
            "end_time": data.end_time.isoformat(),
            "priority_score": Decimal(str(data.priority_score))
        }
        print("💾 保存データ:", item)

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

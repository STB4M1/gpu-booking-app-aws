import json
import boto3
import hashlib
import os
import base64

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Users")

def hash_password(password: str, salt: bytes = None) -> (str, str):
    if not salt:
        salt = os.urandom(16)  # 16バイトのランダムソルト
    hashed = hashlib.pbkdf2_hmac(
        'sha256',                 # ハッシュアルゴリズム
        password.encode('utf-8'), # パスワードをバイト列に
        salt,
        100_000                   # 繰り返し回数（推奨：>=100,000）
    )
    # base64にしてJSON保存しやすくする
    return base64.b64encode(salt).decode('utf-8'), base64.b64encode(hashed).decode('utf-8')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        username = body.get("username")
        password = body.get("password")

        if not username or not password:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "usernameとpasswordは必須です"})
            }

        # ユーザー重複チェック
        existing = table.get_item(Key={"username": username})
        if "Item" in existing:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "このユーザー名は既に登録されています"})
            }

        # パスワードハッシュ化
        salt, hashed_pw = hash_password(password)

        # 保存
        table.put_item(Item={
            "username": username,
            "salt": salt,
            "hashed_password": hashed_pw,
            "is_admin": False
        })

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "ユーザー登録成功！🎉"})
        }

    except Exception as e:
        print("❌ 登録エラー:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

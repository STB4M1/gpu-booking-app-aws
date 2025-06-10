import json
import boto3
import hashlib
import base64

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Users")

def hash_password(password: str, salt: bytes) -> str:
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100_000
    )
    return base64.b64encode(hashed).decode('utf-8')

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

        # ユーザー取得
        result = table.get_item(Key={"username": username})
        user = result.get("Item")

        if not user:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "ユーザーが存在しません"})
            }

        # saltとハッシュの照合
        salt = base64.b64decode(user["salt"])
        expected_hash = user["hashed_password"]
        actual_hash = hash_password(password, salt)

        if actual_hash != expected_hash:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "パスワードが正しくありません"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "ログイン成功！🔓"})
        }

    except Exception as e:
        print("❌ ログインエラー:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
import json
import boto3
import hashlib
import base64
import time

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Users")

def hash_password(password: str, salt: bytes) -> str:
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100_000
    )
    return base64.b64encode(hashed).decode('utf-8')

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

        # ユーザー取得
        result = table.get_item(Key={"username": username})
        user = result.get("Item")

        if not user:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "ユーザーが存在しません"})
            }

        # saltとハッシュの照合
        salt = base64.b64decode(user["salt"])
        expected_hash = user["hashed_password"]
        actual_hash = hash_password(password, salt)

        if actual_hash != expected_hash:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "パスワードが正しくありません"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "ログイン成功！🔓",
                "token": f"{username}-{int(time.time())}"
            })
        }

    except Exception as e:
        print("❌ ログインエラー:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

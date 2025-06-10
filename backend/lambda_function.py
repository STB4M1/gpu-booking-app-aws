import json
from analyze_and_save_handler import lambda_handler as analyze_and_save
from get_reservations_handler import lambda_handler as get_reservations
from confirm_reject_handler import lambda_handler as confirm_reject
from cancel_handler import lambda_handler as cancel_reservation
from register_user_handler import lambda_handler as register_user
from login_user_handler import lambda_handler as login_user
from get_pending_conflicts_handler import lambda_handler as get_pending_conflicts

def lambda_handler(event, context):
    try:
        method = event.get("requestContext", {}).get("http", {}).get("method", "")
        body = json.loads(event.get("body", "{}")) if event.get("body") else {}
        query = event.get("queryStringParameters", {}) or {}
        action = body.get("action") or query.get("action")

        print("🧪 event received:", json.dumps(event))
        print("🧪 method:", method)
        print("🧪 action:", action)

        if action == "analyze" and method == "POST":
            return analyze_and_save(event, context)

        elif action == "get_reservations" and method == "GET":
            return get_reservations(event, context)

        elif action == "get_pending_conflicts" and method == "POST":
            return get_pending_conflicts(event, context)

        elif action == "confirm_reject" and method == "POST":
            return confirm_reject(event, context)

        elif action == "cancel" and method in ["POST", "DELETE"]:
            return cancel_reservation(event, context)

        elif action == "register" and method == "POST":
            return register_user(event, context)

        elif action == "login" and method == "POST":
            print("🔐 login_user ハンドラ呼び出し")
            return login_user(event, context)

        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"無効なactionまたはmethod: {action}, {method}"})
            }

    except Exception as e:
        print("❌ Lambda内例外:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Lambda内エラー: {str(e)}"})
        }

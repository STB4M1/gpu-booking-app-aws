import json
import boto3

# Bedrock クライアントを初期化
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def build_prompt(natural_text: str) -> str:
    """自然文から構造化を促すプロンプトを生成"""
    return f"""
以下の自然文を読み取り、次の形式で予約情報をJSONとして出力してください。

注意：
- 入力から明確に読み取れない情報（開始時間・終了時間・目的・サーバー名など）がある場合は、推測せず null または空文字 "" にしてください。
- 絶対に勝手な補完や仮定をしないでください。
- 出力はJSON形式のみで、余計な説明文や装飾を含めないでください。

特に「priority_score（優先度）」は、以下のルールを参考に0.0〜1.0の範囲で適切に判断してください：

【優先度の判断基準】
・締め切りが早い → 高く評価
・研究のインパクトが大きい → 高く評価
・外部資金がある → 高く評価
・自己学習目的 → 優先度を下げる
・緊急性が高い → 高く評価

【出力形式】
{{
  "start_time": "2025-06-01T08:00:00",
  "end_time": "2025-06-01T10:00:00",
  "purpose": "共同研究のための学習実験",
  "priority_score": 0.85,
  "server_name": "A100",
  "received_text": "{natural_text}"
}}

自然文: {natural_text}
"""

def extract_json(text: str) -> dict:
    """出力されたテキストからJSON部分だけを抽出"""
    try:
        if text.startswith("```json"):
            text = text.removeprefix("```json").removesuffix("```").strip()
        elif text.startswith("```"):
            text = text.removeprefix("```").removesuffix("```").strip()
        json_start = text.find("{")
        json_end = text.rfind("}") + 1
        return json.loads(text[json_start:json_end])
    except Exception as e:
        print("❌ JSON抽出エラー:", e)
        return {}

def analyze_text_with_bedrock(natural_text: str) -> dict:
    """Bedrock Claude (nova-lite) を使って自然文を構造化"""
    prompt = build_prompt(natural_text)
    print("📨 Prompt:\n", prompt)

    response = bedrock.invoke_model(
        modelId="amazon.nova-lite-v1:0",
        body=json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())
    print("🧠 Bedrock 応答:\n", response_body)

    content = response_body["output"]["message"]["content"][0]["text"]
    return extract_json(content)

# GPU予約アプリ（自然言語対応AI予約システム）

自然言語でGPUサーバーの予約ができるアプリです！  
AI（Bedrock Claude）によって優先度を判定し、重複予約の際には譲り合いロジックも搭載！

---

## 主な特徴

- 自然文で「〇月〇日の午前10時からA100を使いたい」と入力するだけ
- AIがジョブ内容から **priority_score（優先度）** を算出
- DynamoDBで予約を管理し、重複を避けるスマートな処理
- 予約が競合したら、他ユーザーと譲り合い確認できるUI搭載
- トークンベースの認証付きログイン/新規登録機能あり

---

## システム構成

```plaintext
Flutter（frontend/booking_app）  
  └── Login / Register / Booking / Conflictページ

AWS Lambda + API Gateway（backend/）  
  └── analyze_text, register_user, login_user などの各ハンドラー

Bedrock Claude（自然文解析）
  └── Bedrockで入力文を構造化し、目的と優先度を推定

DynamoDB
  └── GpuReservations, Users テーブル

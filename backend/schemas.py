from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# --- 構造化予約用リクエスト ---
class NaturalTextRequest(BaseModel):
    text: str

# --- 構造化予約のレスポンス ---
class StructuredReservationResponse(BaseModel):
    start_time: str
    end_time: str
    purpose: str
    priority_score: float

# --- DynamoDBに保存する予約情報（保存時） ---
class ReservationCreate(BaseModel):
    user_id: str
    start_time: datetime
    end_time: datetime
    purpose: str
    server_name: str
    priority_score: Optional[float] = None
    received_text: Optional[str] = None

# --- 予約レスポンス（取得時） ---
class ReservationResponse(BaseModel):
    id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    purpose: str
    priority_score: float
    status: str
    received_text: Optional[str] = None
    server_name: Optional[str] = None
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# --- 構造化予約用リクエスト ---
class NaturalTextRequest(BaseModel):
    text: str

# --- 構造化予約のレスポンス ---
class StructuredReservationResponse(BaseModel):
    start_time: str
    end_time: str
    purpose: str
    priority_score: float

# --- DynamoDBに保存する予約情報（保存時） ---
class ReservationCreate(BaseModel):
    user_id: str
    start_time: datetime
    end_time: datetime
    purpose: str
    server_name: str
    priority_score: Optional[float] = None
    received_text: Optional[str] = None

# --- 予約レスポンス（取得時） ---
class ReservationResponse(BaseModel):
    id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    purpose: str
    priority_score: float
    status: str
    received_text: Optional[str] = None
    server_name: Optional[str] = None

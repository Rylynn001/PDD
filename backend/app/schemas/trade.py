from pydantic import BaseModel
from typing import Any


class TradeRequest(BaseModel):
    anti: str
    cookie: str
    start_date: str   # 格式: 2026-04-01
    end_date: str     # 格式: 2026-04-30


class TradeResponse(BaseModel):
    total: int
    data: list[dict[str, Any]]

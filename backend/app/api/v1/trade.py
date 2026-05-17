import asyncio
import random
import tempfile
from datetime import date, timedelta

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.trade import TradeRequest, TradeResponse
from app.services.browser_service import capture_auth
from app.services.trade_service import fetch_trade_data

router = APIRouter(prefix="/trade", tags=["trade"])


def _date_chunks(start_date: str, end_date: str) -> list[tuple[str, str]]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    chunks = []
    cur = start
    while cur <= end:
        chunk_end = min(cur + timedelta(days=29), end)
        chunks.append((cur.isoformat(), chunk_end.isoformat()))
        cur = chunk_end + timedelta(days=1)
    return chunks


async def _fetch_all(req: TradeRequest) -> list[dict]:
    chunks = _date_chunks(req.start_date, req.end_date)
    all_data = []

    try:
        auth = await capture_auth()
        anti, cookie = auth["anti"], auth["cookie"]
    except Exception:
        anti, cookie = req.anti, req.cookie

    for i, (chunk_start, chunk_end) in enumerate(chunks):
        if i > 0:
            await asyncio.sleep(random.uniform(2, 5))
            try:
                auth = await capture_auth()
                anti = auth["anti"]
                cookie = auth["cookie"]
            except Exception:
                pass

        data = fetch_trade_data(anti, cookie, chunk_start, chunk_end)
        all_data.extend(data)

    return all_data


@router.post("/query", response_model=TradeResponse)
async def query_trade(req: TradeRequest):
    data = await _fetch_all(req)
    return {"total": len(data), "data": data}


@router.post("/query/excel")
async def query_trade_excel(req: TradeRequest):
    data = await _fetch_all(req)
    if not data:
        raise HTTPException(status_code=404, detail="没有符合条件的数据")

    df = pd.DataFrame(data)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(tmp.name, index=False, engine="openpyxl")
    filename = f"pdd_trade_{req.start_date}_{req.end_date}.xlsx"
    return FileResponse(
        tmp.name,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

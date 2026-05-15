import tempfile
import pandas as pd
from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.schemas.trade import TradeRequest, TradeResponse
from app.services.trade_service import fetch_trade_data

router = APIRouter(prefix="/trade", tags=["trade"])


@router.post("/query", response_model=TradeResponse)
def query_trade(req: TradeRequest):
    data = fetch_trade_data(req.anti, req.cookie, req.start_date, req.end_date)
    return {"total": len(data), "data": data}


@router.post("/query/excel")
def query_trade_excel(req: TradeRequest):
    data = fetch_trade_data(req.anti, req.cookie, req.start_date, req.end_date)
    if not data:
        from fastapi import HTTPException
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

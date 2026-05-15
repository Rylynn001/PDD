import requests
import json
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tempfile
import os

app = FastAPI()

API_URL = "https://mms.pinduoduo.com/sydney/api/mallTrade/queryMallTradeList"

FIELDS_MAPPING = {
    'stateDate': '日期',
    'payOrdrAmt': '成交金额',
    'payOrdrCnt': '成交订单数',
    'payOrdrUsrCnt': '成交买家数',
    'payUvRto': '成交转化率(%)',
    'payOrdrAup': '客单价',
    'rpayUsrRtoDth': '成交老买家占比(%)',
    'mallFavCnt': '店铺关注用户数',
    'sucRfOrdrAmt1d': '退款金额',
    'sucRfOrdrCnt1d': '退款单数',
    'uvCfmVal': '平均访客价值'
}


class TradeRequest(BaseModel):
    anti: str
    cookie: str
    start_date: str  # 格式: 2026-04-01
    end_date: str    # 格式: 2026-04-30


def filter_data(raw_data, start_date, end_date):
    filtered_list = []
    items = raw_data if isinstance(raw_data, list) else [raw_data] if isinstance(raw_data, dict) else []

    for item in items:
        item_date = item.get('stateDate', '')
        if not (start_date <= item_date <= end_date):
            continue
        filtered_item = {}
        for key, chinese_name in FIELDS_MAPPING.items():
            if key in item:
                value = item[key]
                if key in ('payUvRto', 'rpayUsrRtoDth') and value is not None:
                    value = round(value * 100, 2)
                filtered_item[chinese_name] = value
        if filtered_item:
            filtered_list.append(filtered_item)

    return filtered_list


def extract_raw_data(data):
    if 'result' in data and isinstance(data['result'], dict):
        result = data['result']
        for key in ('dayList', 'list', 'data'):
            if key in result:
                return result[key]
        return result
    if 'result' in data and isinstance(data['result'], list):
        return data['result']
    if 'data' in data:
        return data['data']
    return data


@app.post("/query")
def query_trade(req: TradeRequest):
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json",
        "origin": "https://mms.pinduoduo.com",
        "referer": "https://mms.pinduoduo.com/sycm/stores_data/operation",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "anti-content": req.anti,
        "cookie": req.cookie,
    }
    payload = {
        "queryType": 7,
        "queryDate": req.end_date,
        "startDate": req.start_date,
        "endDate": req.end_date,
    }

    resp = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="上游接口请求失败")

    data = resp.json()
    raw_data = extract_raw_data(data)
    filtered = filter_data(raw_data, req.start_date, req.end_date)
    return {"total": len(filtered), "data": filtered}


@app.post("/query/excel")
def query_trade_excel(req: TradeRequest):
    result = query_trade(req)
    filtered = result["data"]
    if not filtered:
        raise HTTPException(status_code=404, detail="没有符合条件的数据")

    df = pd.DataFrame(filtered)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(tmp.name, index=False, engine="openpyxl")
    filename = f"pdd_trade_{req.start_date}_{req.end_date}.xlsx"
    return FileResponse(tmp.name, filename=filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

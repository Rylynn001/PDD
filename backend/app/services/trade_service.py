import json
import requests
from fastapi import HTTPException

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
    'uvCfmVal': '平均访客价值',
}


def fetch_trade_data(anti: str, cookie: str, start_date: str, end_date: str) -> list[dict]:
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json",
        "origin": "https://mms.pinduoduo.com",
        "referer": "https://mms.pinduoduo.com/sycm/stores_data/operation",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/146.0.0.0 Safari/537.36"
        ),
        "anti-content": anti,
        "cookie": cookie,
    }
    payload = {
        "queryType": 7,
        "queryDate": end_date,
        "startDate": start_date,
        "endDate": end_date,
    }

    resp = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=15)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="上游接口请求失败")

    data = resp.json()
    raw = _extract_raw(data)
    return _filter(raw, start_date, end_date)


def _extract_raw(data: dict):
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


def _filter(raw_data, start_date: str, end_date: str) -> list[dict]:
    items = raw_data if isinstance(raw_data, list) else ([raw_data] if isinstance(raw_data, dict) else [])
    result = []
    for item in items:
        item_date = item.get('stateDate', '')
        if not (start_date <= item_date <= end_date):
            continue
        row = {}
        for key, label in FIELDS_MAPPING.items():
            if key not in item:
                continue
            value = item[key]
            if key in ('payUvRto', 'rpayUsrRtoDth') and value is not None:
                value = round(value * 100, 2)
            row[label] = value
        if row:
            result.append(row)
    return result

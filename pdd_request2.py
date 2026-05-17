import requests
import json
import pandas as pd
from datetime import datetime

# 接口 URL
url = "https://mms.pinduoduo.com/sydney/api/mallTrade/queryMallTradeList"
ANTI = "0asWfqnd0jGaj99p9I4zjuSWzlGMoW_3hQvdh86ynPQgwImlfdypAfS7Ef5giogIDnhET75LZiauJkjA6pTzAaAUl9IqnjyJ666375lb8Eaap_la8VCTcRQZf9gFyhzdm4k0LQdiI6684TDlDrH8QBZ6r-Y3-uYLqV5gqWascYlR8lUcOIoniomF515G4K5dHsDj5w3piTy7XPtx-5wq5WHMI-iU1RO-tT7CXGLrP1TDFssTt2VkXvOBesU6eZPT2zT4D1u9eFIsygi0t-UllXh5Ds_yK__4VHAccrorTftkV3KlCDXsdsYMMjYK45H9oK2Bs5hn_WEFv7206jXFAFxsCRXPHj0ivsI6m7lZ3kly29kHc1nG0u3oCLJuaJRQKNqUapamIO3zNe0te2-fDBfjN9ibJxwiLHvRbN6EUmEcC68YGJaHrSun3rPVY0PFXMGE"
Cookie = "api_uid=CkwtS2n/95xlxgB8LWjvAg==; _nano_fp=Xpm8l0XJX5mYl0TJlT_yaDGjVaTi0V0Wf6KxafxU; rckk=eZOzMe88Jfcr6ClNgxMGNoQbTxcb4yKt; _bee=eZOzMe88Jfcr6ClNgxMGNoQbTxcb4yKt; ru1k=713c0e0a-c210-4352-a6df-aee16e9e48ab; _f77=713c0e0a-c210-4352-a6df-aee16e9e48ab; ru2k=16352dec-ca30-4f17-88c4-61b0a3f63109; _a42=16352dec-ca30-4f17-88c4-61b0a3f63109; PASS_ID=1-fEAHUwJPuRwuCFTvEjp3UWQowmesJnofdecgzEV6yw9tm3at00YtNU5gT+PEfpiEqa7VC7MXxHmGKeG8JjuHpg_837371075_183951330; windows_app_shop_token_23=eyJ0IjoiU3NrcEwxUHZmSE1kYUJGMGZKY3RacVZUMzUyZWlFWG94WCtwOVJkTnlxWGpYZlZxQnY2MUhvdkpMb010anhGeiIsInYiOjEsInMiOjIzLCJtIjo4MzczNzEwNzUsInUiOjE4Mzk1MTMzMH0; mms_b84d1838=3616,110,3700,3706,3523,3660,3709,3614,3447,3599,3658,3605,3621,3622,3669,3677,3588,3254,3531,3474,3475,3477,3479,3497,3687,3482,1202,1203,1204,1205,3417; x-visit-time=1778384635486; JSESSIONID=A0340BA5ABB6A2FD13D54B7943819877"
StartDate = "2026-04-01"
EndDate = "2026-04-30"
# 请求头
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json",
    "origin": "https://mms.pinduoduo.com",
    "referer": "https://mms.pinduoduo.com/sycm/stores_data/operation",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "anti-content": ANTI,
    "cookie": Cookie
}

# 请求参数
payload = {
    "queryType": 7,
    "queryDate": EndDate,
    "startDate": StartDate,
    "endDate": EndDate
}

def filter_data_for_excel(raw_data, start_date, end_date):
    """
    筛选数据，保留主要指标，排除对比和预测字段，并按日期范围过滤
    """
    # 定义需要保留的字段及其中文名称
    fields_mapping = {
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

    filtered_list = []

    # 如果是列表数据
    if isinstance(raw_data, list):
        for item in raw_data:
            # 检查日期是否在范围内
            item_date = item.get('stateDate', '')
            if item_date < start_date or item_date > end_date:
                print(f"跳过日期: {item_date} (不在范围 {start_date} 到 {end_date} 内)")
                continue

            filtered_item = {}
            for key, chinese_name in fields_mapping.items():
                if key in item:
                    value = item[key]
                    # 转化率和占比转换为百分比
                    if key in ['payUvRto', 'rpayUsrRtoDth'] and value is not None:
                        value = round(value * 100, 2)
                    filtered_item[chinese_name] = value
            if filtered_item:  # 只添加非空的数据
                filtered_list.append(filtered_item)
    # 如果是单个字典
    elif isinstance(raw_data, dict):
        item_date = raw_data.get('stateDate', '')
        if start_date <= item_date <= end_date:
            filtered_item = {}
            for key, chinese_name in fields_mapping.items():
                if key in raw_data:
                    value = raw_data[key]
                    # 转化率和占比转换为百分比
                    if key in ['payUvRto', 'rpayUsrRtoDth'] and value is not None:
                        value = round(value * 100, 2)
                    filtered_item[chinese_name] = value
            if filtered_item:
                filtered_list.append(filtered_item)

    return filtered_list

def save_to_excel(data_list, filename=None):
    """
    将筛选后的数据保存到Excel
    """
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'pdd_data_{timestamp}.xlsx'

    df = pd.DataFrame(data_list)
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"数据已保存到: {filename}")
    return filename

# 发送 POST 请求
response = requests.post(url, headers=headers, data=json.dumps(payload))

# 输出返回内容
if response.status_code == 200:
    data = response.json()
    print("原始数据:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # 根据实际API返回结构提取数据列表
    raw_data = None
    if 'result' in data and isinstance(data['result'], dict):
        # 尝试从result中找到列表数据
        if 'dayList' in data['result']:
            raw_data = data['result']['dayList']
        elif 'list' in data['result']:
            raw_data = data['result']['list']
        elif 'data' in data[      'result']:
            raw_data = data['result']['data']
        else:
            raw_data = data['result']
    elif 'result' in data and isinstance(data['result'], list):
        raw_data = data['result']
    elif 'data' in data:
        raw_data = data['data']
    else:
        raw_data = data

    print(f"\n提取的数据类型: {type(raw_data)}")
    if isinstance(raw_data, list):
        print(f"数据条数: {len(raw_data)}")

    # 筛选数据，传入日期范围
    filtered_data = filter_data_for_excel(raw_data, payload['startDate'], payload['endDate'])
    print(f"\n筛选后的数据条数: {len(filtered_data)}")
    print("筛选后的数据:")
    print(json.dumps(filtered_data, ensure_ascii=False, indent=2))

    # 保存到Excel
    if filtered_data:
        save_to_excel(filtered_data)
    else:
        print("警告: 没有符合条件的数据可以保存")
else:
    print(f"请求失败，状态码：{response.status_code}")
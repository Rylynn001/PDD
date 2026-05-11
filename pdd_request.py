import requests
import json

# -------------------------------
# ⚠️ 请手动更新 Cookie 和 crawlerInfo
# -------------------------------
COOKIE = "api_uid=CkwtS2n/95xlxgB8LWjvAg==; _nano_fp=Xpm8l0XJX5mYl0TJlT_yaDGjVaTi0V0Wf6KxafxU; rckk=eZOzMe88Jfcr6ClNgxMGNoQbTxcb4yKt; _bee=eZOzMe88Jfcr6ClNgxMGNoQbTxcb4yKt; ru1k=713c0e0a-c210-4352-a6df-aee16e9e48ab; _f77=713c0e0a-c210-4352-a6df-aee16e9e48ab; ru2k=16352dec-ca30-4f17-88c4-61b0a3f63109; _a42=16352dec-ca30-4f17-88c4-61b0a3f63109; PASS_ID=1-fEAHUwJPuRwuCFTvEjp3UWQowmesJnofdecgzEV6yw9tm3at00YtNU5gT+PEfpiEqa7VC7MXxHmGKeG8JjuHpg_837371075_183951330; windows_app_shop_token_23=eyJ0IjoiU3NrcEwxUHZmSE1kYUJGMGZKY3RacVZUMzUyZWlFWG94WCtwOVJkTnlxWGpYZlZxQnY2MUhvdkpMb010anhGeiIsInYiOjEsInMiOjIzLCJtIjo4MzczNzEwNzUsInUiOjE4Mzk1MTMzMH0; mms_b84d1838=3616,110,3700,3706,3523,3660,3709,3614,3447,3599,3658,3605,3621,3622,3669,3677,3588,3254,3531,3474,3475,3477,3479,3497,3687,3482,1202,1203,1204,1205,3417; x-visit-time=1778384635486; JSESSIONID=A0340BA5ABB6A2FD13D54B7943819877"
CRAWLER_INFO = "0asAfqnygcKgygE2W4uVl2-1JUYEZFoFIGfD1HuYmE_rdnKLdlg3-zg-hjMncjMu8CcHMJ5tztv_5RcCwZg_os2yEXSBLKVyKnE0bP6y7K12khAQsT1PZpj_W9Iq9YNEQZWYQaSV0VhmloTv33lvZ4JyDUsrL4jlmpcNxWT2SV0oyDoaDcb67yB6Rsvc9mRxVWw30Y5jo9qIK2Qm97u23W5zv_clbjAjD8BnOsv7geC3MoYgYR9smqhGq0h0UEHaB8OHqqVP8bhsifmnRTvIgvi3KwOY7w4lSnNLoZYAG9tyz-NWVvaszCC9-uaR5naBkAR9rW3jla5bSrxIC7szKQdu1JynR9SQY23gJsrWl9NOXoHia2KWDqlNTrt6azJTGfyUtISwSYCidbtVMjrEuuymZmerG0lDXgHLDkTeqYS0v60KG1W8okXXzESP0HFMpSIklQmNdWQ8-oG0pX6hxK-zzql53BbBKJsbjgjsKHgEM1d-wweFMp-7GFjBiOuCIMvYnPsvBwirff1zeKVZyd_YX0sDXPUe3XFPKDssVP65cw45KHdwn1mjLPelcxURKPmUEzU4VS8u47rAFNTqqxTyFSj9MO56_Qan51gf4dOjZD1jaxcYQardV3M7vhjxBxJvHE6G06eD_z6_cIeYcBy-UpscfVx-fL5eZwpdWRuS46WWUqG3dj6z0rmdeUaR3OuP_b7HztR7AJnUPLJ3wlf2jnvcn_aC80S0DAfcVl2QYkz3QDPFXMGW"

# 请求 URL
URL = "https://mms.pinduoduo.com/sydney/api/goodsDataShow/queryGoodsPagePlnOstListByDate"

# 请求头
HEADERS = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://mms.pinduoduo.com",
    "Referer": "https://mms.pinduoduo.com/sycm/goods_effect?msfrom=mms_sidenav",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Cookie": COOKIE,
    "anti-content": CRAWLER_INFO
}

# 请求体参数
DATA = {
    "queryType": 7,
    "startDate": "2026-04-01",
    "endDate": "2026-04-30",
    "queryDate": "2026-04-30",
    "crawlerInfo": CRAWLER_INFO
}

def fetch_goods_data():
    try:
        response = requests.post(URL, headers=HEADERS, json=DATA, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 简单处理
        if data.get("success"):
            print("请求成功！数据条数:", len(data.get("result", [])))
            # 输出前几条数据做测试
            for item in data.get("result", [])[:3]:
                print(json.dumps(item, ensure_ascii=False, indent=2))
        else:
            print("接口返回失败:", data.get("errorMsg"))

    except requests.exceptions.RequestException as e:
        print("请求异常:", e)

if __name__ == "__main__":
    fetch_goods_data()
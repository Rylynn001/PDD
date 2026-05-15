import asyncio
from playwright.async_api import async_playwright, BrowserContext, Page

_playwright = None
_context: BrowserContext | None = None
_page: Page | None = None


async def start_browser():
    global _playwright, _context, _page
    _playwright = await async_playwright().start()
    _context = await _playwright.chromium.launch_persistent_context(
        user_data_dir="./pdd_browser/user_data",
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    pages = _context.pages
    _page = pages[0] if pages else await _context.new_page()
    await _page.goto("https://mms.pinduoduo.com")


async def stop_browser():
    global _playwright, _context, _page
    if _context:
        await _context.close()
    if _playwright:
        await _playwright.stop()
    _context = None
    _page = None
    _playwright = None


async def capture_auth() -> dict[str, str]:
    """在浏览器上下文内发起一次真实请求，拦截并返回 anti-content 和 cookie"""
    if _context is None or _page is None:
        raise RuntimeError("浏览器未启动")

    captured: dict[str, str] = {}
    event = asyncio.Event()

    TARGET = "https://mms.pinduoduo.com/sydney/api/mallTrade/queryMallTradeList"

    async def handle_route(route):
        req = route.request
        headers = await req.all_headers()
        captured["anti"] = headers.get("anti-content", "")
        captured["cookie"] = headers.get("cookie", "")
        event.set()
        await route.abort()  # 拦截即止，不真正发出

    await _context.route(TARGET, handle_route)
    try:
        # 在页面上下文内触发一次请求，让浏览器自动注入 cookie 和 anti-content
        await _page.evaluate(
            """(url) => fetch(url, {
                method: 'POST',
                headers: {'content-type': 'application/json'},
                body: JSON.stringify({queryType:7, queryDate:'2026-01-01', startDate:'2026-01-01', endDate:'2026-01-01'})
            }).catch(() => {})""",
            TARGET,
        )
        await asyncio.wait_for(event.wait(), timeout=10)
    finally:
        await _context.unroute(TARGET, handle_route)

    if not captured.get("anti") and not captured.get("cookie"):
        raise RuntimeError("未能捕获认证信息，请确认浏览器已登录拼多多商家后台")

    return captured

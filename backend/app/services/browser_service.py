import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright, BrowserContext, Page

_executor = ThreadPoolExecutor(max_workers=1)
_playwright = None
_context: BrowserContext | None = None
_page: Page | None = None

TARGET = "https://mms.pinduoduo.com/sydney/api/mallTrade/queryMallTradeList"


def _do_start():
    global _playwright, _context, _page
    _playwright = sync_playwright().start()
    _context = _playwright.chromium.launch_persistent_context(
        user_data_dir="./pdd_browser/user_data",
        headless=False,
        channel="chrome",
        args=["--disable-blink-features=AutomationControlled"],
    )
    pages = _context.pages
    _page = pages[0] if pages else _context.new_page()
    _page.goto("https://mms.pinduoduo.com")


def _do_stop():
    global _playwright, _context, _page
    if _context:
        _context.close()
    if _playwright:
        _playwright.stop()
    _context = None
    _page = None
    _playwright = None


def _do_capture() -> dict[str, str]:
    if _context is None or _page is None:
        raise RuntimeError("浏览器未启动")

    captured: dict[str, str] = {}
    done = threading.Event()

    # CDP 协议可以拿到浏览器内核层实际发出的完整请求头（和 Chrome DevTools 看到的一致）
    cdp = _context.new_cdp_session(_page)
    cdp.send("Network.enable")

    def on_extra_info(params):
        if done.is_set():
            return
        headers = {k.lower(): v for k, v in params.get("headers", {}).items()}
        anti = headers.get("anti-content", "")
        if anti:
            captured["anti"] = anti
            captured["cookie"] = headers.get("cookie", "")
            done.set()

    cdp.on("Network.requestWillBeSentExtraInfo", on_extra_info)

    try:
        _page.goto("https://mms.pinduoduo.com/home/", wait_until="domcontentloaded")
        done.wait(timeout=15)
    finally:
        try:
            cdp.detach()
        except Exception:
            pass

    if not captured.get("anti"):
        raise RuntimeError("未能捕获 anti-content，请确认浏览器已登录拼多多商家后台")

    return captured


async def start_browser():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_executor, _do_start)


async def stop_browser():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_executor, _do_stop)


async def capture_auth() -> dict[str, str]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _do_capture)

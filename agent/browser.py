from __future__ import annotations
import asyncio
import os
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page


class BrowserController:
    def __init__(self, browser_name: str = "chromium", headless: bool = False):
        self.browser_name = browser_name
        self.headless = headless
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None

    async def __aenter__(self) -> "BrowserController":
        await self.launch()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def launch(self) -> None:
        if self._browser:
            return
        pw = await async_playwright().start()
        launcher = getattr(pw, self.browser_name)
        launch_kwargs = {"headless": self.headless}
        # Allow using Chrome channel explicitly via env
        chrome_channel = os.getenv("CHROME_CHANNEL")
        if chrome_channel and self.browser_name == "chromium":
            launch_kwargs["channel"] = chrome_channel  # e.g., "chrome", "chrome-beta"
        self._browser = await launcher.launch(**launch_kwargs)
        context = await self._browser.new_context(viewport={"width": 1280, "height": 800})
        self._page = await context.new_page()

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._page = None

    @property
    def page(self) -> Page:
        if not self._page:
            raise RuntimeError("Browser not launched")
        return self._page

    async def goto(self, url: str) -> None:
        await self.page.goto(url)

    async def click(self, selector: str) -> None:
        await self.page.click(selector)

    async def fill(self, selector: str, value: str) -> None:
        await self.page.fill(selector, value)

    async def wait_for_selector(self, selector: str, timeout_ms: int = 15000) -> None:
        await self.page.wait_for_selector(selector, timeout=timeout_ms)

    async def text_content(self, selector: str) -> str:
        await self.wait_for_selector(selector)
        content = await self.page.text_content(selector)
        return content or ""


async def quick_demo():
    browser_name = os.getenv("BROWSER", "chromium")
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    async with BrowserController(browser_name, headless) as bc:
        await bc.goto("https://example.com")
        h1 = await bc.text_content("h1")
        print("Page heading:", h1)


if __name__ == "__main__":
    asyncio.run(quick_demo())

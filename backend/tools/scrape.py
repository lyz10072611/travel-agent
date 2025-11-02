from firecrawl import FirecrawlApp, ScrapeOptions
import os
from agno.tools import tool
from loguru import logger
from config.logger import logger_hook

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))


@tool(
    name="scrape_website",
    description="抓取网站并返回markdown内容。",
    tool_hooks=[logger_hook],
)
def scrape_website(url: str) -> str:
    """抓取网站并返回markdown内容。

    参数:
        url (str): 要抓取的网站URL。

    返回:
        str: 网站的markdown内容。

    示例:
        >>> scrape_website("https://www.google.com")
        "## Google"
    """
    scrape_status = app.scrape_url(
        url,
        formats=["markdown"],
        wait_for=30000,
        timeout=60000,
    )
    return scrape_status.markdown

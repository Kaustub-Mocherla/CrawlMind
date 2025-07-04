import sys
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

sys.stdout.reconfigure(encoding='utf-8')

async def crawl_url(url):
    browser_config = BrowserConfig(verbose=True)
    run_config = CrawlerRunConfig(
        word_count_threshold=0,          
        excluded_tags=[],               
        exclude_external_links=False,
        process_iframes=True,
        remove_overlay_elements=True,
        cache_mode=CacheMode.ENABLED
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)
        if result.success and result.markdown.strip():
            with open("crawled_content.md", "w", encoding="utf-8") as f:
                f.write(result.markdown)
            print("Crawl succeeded. Content saved to crawled_content.md")
        else:
            print(f"ERROR: Crawl failed or returned no content: {result.error_message}")

if __name__ == "__main__":
    url = sys.argv[1]
    asyncio.run(crawl_url(url))

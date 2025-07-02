import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def crawl_website(url_recived: str):
    browser_config = BrowserConfig()
    run_config = CrawlerRunConfig(
        remove_overlay_elements=True,
        word_count_threshold=20,
        exclude_external_links=True,
        process_iframes=True,
        excluded_tags=['form','header'],
        cache_mode=CacheMode.ENABLED
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url = url_recived,
            config=run_config
            )
        print("Crawl Result",result.markdown)
        return result

if __name__ == "__main__":
    asyncio.run(crawl_website("https://example.com"))
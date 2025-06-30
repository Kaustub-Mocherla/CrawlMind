import asyncio
from crawl4ai import *

async def main():
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
            url = "https://books.toscrape.com/",
            config=run_config
            )
        
        if result.success:
            print(f"Content : {result.markdown[:500]}")
        for image in result.media["images"]:
            print(f"Found Images:{image['src']}")
        for link in result.links["internal"]:
            print(f"Internal Links : {link['href']}")

        else:
            print(f"Crawl Failed:{result.error_message}")
            print(f"Status Code : {result.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
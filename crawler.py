import sys
import os
import asyncio
import time
import atexit
import traceback
import requests
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

# Ensure UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Output file path - use absolute path to avoid issues
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crawled_content.md")

# Cleanup function to ensure resources are released
def cleanup():
    try:
        tasks = asyncio.all_tasks() if hasattr(asyncio, 'all_tasks') else asyncio.Task.all_tasks()
        for task in tasks:
            task.cancel()
    except Exception as e:
        print(f"Cleanup error: {e}")

atexit.register(cleanup)

def fallback_scrape(url):
    """Fallback scraper using requests + BeautifulSoup"""
    print("Using fallback scraper...")
    try:
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            print(f"Fallback failed: HTTP {response.status_code}")
            return ""
        soup = BeautifulSoup(response.text, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines()]
        text = "\n".join(line for line in lines if line)
        print(f"Fallback scrape length: {len(text)} characters")
        return text
    except Exception as e:
        print(f"Fallback scrape error: {e}")
        traceback.print_exc()
        return ""

async def crawl_url(url):
    print(f"Crawling URL: {url}")
    content_to_save = ""

    try:
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

            print(f"RESULT SUCCESS: {result.success}")
            print(f"RESULT ERROR: {result.error_message}")
            print(f"RESULT MARKDOWN LENGTH: {len(result.markdown.strip())}")

            # If crawl4ai succeeds but returns tiny junk, fallback
            if result.success and len(result.markdown.strip()) > 50:
                content_to_save = result.markdown.strip()
                print("Using crawl4ai output ✅")
            else:
                print("crawl4ai failed or returned too little. Using fallback...")
                fallback = fallback_scrape(url)
                if len(fallback.strip()) > 50:
                    content_to_save = fallback
                else:
                    print("Fallback also failed. No useful content.")
                    return

    except Exception as e:
        print(f"ERROR: Crawler exception: {e}")
        traceback.print_exc()
        print("Trying fallback...")
        fallback = fallback_scrape(url)
        if len(fallback.strip()) > 50:
            content_to_save = fallback
        else:
            print("Fallback also failed. No useful content.")
            return

    # Write content to file if we got valid text
    if content_to_save:
        temp_file = f"{OUTPUT_FILE}.temp"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content_to_save)

            time.sleep(0.5)

            if os.path.exists(OUTPUT_FILE):
                try:
                    os.remove(OUTPUT_FILE)
                except PermissionError:
                    timestamp = int(time.time())
                    fallback_name = f"{OUTPUT_FILE}.{timestamp}"
                    os.rename(temp_file, fallback_name)
                    print(f"Content saved to fallback file: {fallback_name}")
                    return

            os.rename(temp_file, OUTPUT_FILE)
            print(f"Crawl succeeded. Content saved to: {OUTPUT_FILE}")
        except Exception as write_error:
            print(f"ERROR: Failed to write content: {write_error}")
            traceback.print_exc()
    else:
        print("No content to save. Exiting.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: URL argument is required")
        sys.exit(1)

    url = sys.argv[1]
    try:
        asyncio.run(crawl_url(url))
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

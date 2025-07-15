import sys
import os
import asyncio
import time
import atexit
import traceback
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

# Ensure UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Output file path - use absolute path to avoid issues
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crawled_content.md")

# Cleanup function to ensure resources are released
def cleanup():
    try:
        # Make sure any background tasks are cleaned up
        tasks = asyncio.all_tasks() if hasattr(asyncio, 'all_tasks') else asyncio.Task.all_tasks()
        for task in tasks:
            task.cancel()
    except Exception as e:
        print(f"Cleanup error: {e}")

# Register cleanup function
atexit.register(cleanup)

async def crawl_url(url):
    print(f"Crawling URL: {url}")
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
            if result.success and result.markdown.strip():
                # Write to temp file first, then rename to avoid file access issues
                temp_file = f"{OUTPUT_FILE}.temp"
                try:
                    with open(temp_file, "w", encoding="utf-8") as f:
                        f.write(result.markdown)
                    
                    # Give Windows a moment to release file handles
                    time.sleep(0.5)
                    
                    # If output file exists, try to remove it first
                    if os.path.exists(OUTPUT_FILE):
                        try:
                            os.remove(OUTPUT_FILE)
                        except PermissionError:
                            print(f"Warning: Could not remove existing file {OUTPUT_FILE}")
                            # Use a timestamped file instead
                            OUTPUT_FILE_ACTUAL = f"{OUTPUT_FILE}.{int(time.time())}"
                            os.rename(temp_file, OUTPUT_FILE_ACTUAL)
                            print(f"Crawl succeeded. Content saved to {OUTPUT_FILE_ACTUAL}")
                            return
                    
                    # Rename temp file to final file
                    os.rename(temp_file, OUTPUT_FILE)
                    print(f"Crawl succeeded. Content saved to {OUTPUT_FILE}")
                except Exception as write_error:
                    print(f"ERROR: Failed to write content: {write_error}")
                    traceback.print_exc()
            else:
                print(f"ERROR: Crawl failed or returned no content: {result.error_message}")
    except Exception as e:
        print(f"ERROR: Crawler exception: {e}")
        traceback.print_exc()

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
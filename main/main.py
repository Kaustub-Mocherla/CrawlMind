
import streamlit as st
from vectordb.embedder import embedded_chunks
from vectordb.chunks import chunked_markdown
from vectordb.chromedb import chrome_db
from ingestion.crawler import crawl_website
import asyncio


def main():
    st.set_page_config(page_title="CrawlMind", page_icon=":robot:")
    st.title("CrawlMind")

    url = st.text_input("Enter the Website URL:").strip()

    if st.button("Crawl Site"):
        if url:
            st.write("🕷️ Crawling the Website ...")

            # SAFER loop for Streamlit
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(crawl_website(url))

            if result and hasattr(result, 'markdown') and result.markdown:
                st.success("✅ Crawl complete! Chunking + embedding...")

                chunks = chunked_markdown(result.markdown)
                vectors = embedded_chunks(chunks)
                chrome_db(chunks, vectors)

                st.success("🎉 All done! Your crawl data is embedded and stored.")
            else:
                st.error("❌ Failed to crawl the website or no content found.")
        else:
            st.warning("⚠️ Please enter a valid URL.")


if __name__ == "__main__":
    main()

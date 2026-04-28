# utils.py

# from scraper.brecorder_scraper import fetch_stock_related_articles as fetch_brecorder
# from scraper.dawn_scraper import fetch_stock_related_articles as fetch_dawn

from .scraper.brecorder_scraper import fetch_stock_related_articles as fetch_brecorder
from .scraper.dawn_scraper import fetch_stock_related_articles as fetch_dawn

def fetch_all_news():
    """
    Fetches and combines articles from Brecorder and Dawn.
    Returns a unified list of dicts with keys: title, link, summary, content.
    """
    print("📥 Fetching from Brecorder...")
    brecorder_articles = fetch_brecorder()

    print("📥 Fetching from Dawn...")
    dawn_articles = fetch_dawn()

    all_articles = brecorder_articles + dawn_articles
    print(f"✅ Total articles fetched: {len(all_articles)}")

    return all_articles

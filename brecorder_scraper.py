import requests
from bs4 import BeautifulSoup

# Define your target stock keywords
stock_keywords = ["KSE", "OGDC", "PSX", "HBL", "ENGRO", "LUCK", "MCB", "UBL","STOCK", "MARKET", "SHARES", "STOCKS", "BULL", "BEAR", "TRADING", "INVESTMENT"]

def get_article_text(article_url):
    """Fetch the full article body from the article page."""
    try:
        response = requests.get(article_url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        content_div = soup.find("div", class_="story__content")
        if not content_div:
            return "[No article content found]"

        paragraphs = content_div.find_all("p")
        full_text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        return full_text

    except Exception as e:
        return f"[Error fetching article: {e}]"

def fetch_stock_related_articles():
    """Fetch and return stock-related articles (headline + link + full text)."""
    url = "https://www.brecorder.com/markets/stocks"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    seen_links = set()
    articles = []

    for a_tag in soup.find_all("a", class_="story__link"):
        title = a_tag.get_text(strip=True)
        link = a_tag["href"]

        # Avoid duplicates by link
        if link in seen_links:
            continue
        seen_links.add(link)

        # Filter based on keywords
        if any(kw.upper() in title.upper() for kw in stock_keywords):
            print(f"✅ Found stock-related headline: {title}")
            content = get_article_text(link)
            articles.append({
                "title": title,
                "link": link,
                "content": content
            })

    return articles

# === Run it ===
if __name__ == "__main__":
    stock_articles = fetch_stock_related_articles()
    print(f"\n📰 Total PSX/stock-related articles fetched: {len(stock_articles)}\n")

    for article in stock_articles:
        print("🔗", article["title"])
        print(article["link"])
        print(article["content"][:500], "...\n")  # Show preview of first 500 characters

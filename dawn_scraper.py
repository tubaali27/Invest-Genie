import requests
from bs4 import BeautifulSoup

stock_keywords = ["KSE", "OGDC", "PSX", "HBL", "ENGRO", "LUCK", "MCB", "UBL",
                  "STOCK", "MARKET", "SHARES", "STOCKS", "BULL", "BEAR", "TRADING", "INVESTMENT"]

def get_article_text(article_url):
    """Fetch full article body from Dawn News."""
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
    url = "https://www.dawn.com/business"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    articles = []
    seen_links = set()

    for article_tag in soup.find_all("article", class_="story"):
        title_tag = article_tag.find("h2", class_="story__title")
        link_tag = title_tag.find("a") if title_tag else None

        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        link = link_tag["href"]

        if not title or link in seen_links:
            continue
        seen_links.add(link)

        # Extract excerpt
        excerpt_tag = article_tag.find("div", class_="story__excerpt")
        excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else "[No summary]"

        # Filter based on keywords
        title_upper = f" {title.upper()} "
        if any(f" {kw.upper()} " in title_upper for kw in stock_keywords):
            print(f"✅ Found stock-related headline: {title}")
            content = get_article_text(link)

            articles.append({
                "title": title,
                "link": link,
                "summary": excerpt,
                "content": content
            })

    return articles

# === Run It ===
if __name__ == "__main__":
    stock_articles = fetch_stock_related_articles()
    print(f"\n📰 Total Dawn stock-related articles fetched: {len(stock_articles)}\n")

    for article in stock_articles:
        print("🔗", article["title"])
        print(article["link"])
        print("📝", article["summary"])
        print("📄", article["content"], "...\n")

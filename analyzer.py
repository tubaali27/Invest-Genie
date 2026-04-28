from transformers import pipeline

# Load once globally
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

def analyze_sentiment(text: str) -> str:
    # Trim to 512 tokens max (FinBERT’s input limit)
    text = text[:2000]  # ~600-800 tokens
    try:
        result = sentiment_pipeline(text)[0]
        print(f"🧠 FinBERT Output: {result}")
        return result['label'].capitalize()  # e.g., Positive
    except Exception as e:
        print("❌ FinBERT error:", e)
        return "Unknown"

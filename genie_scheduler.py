import sys
import os
from datetime import date, timedelta
import time
import pandas as pd
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from psx_data_reader import data_reader
from dateutil.relativedelta import relativedelta
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase (do this ONCE)
cred = credentials.Certificate("d:/stock_genie/stock_genie.json")  # <-- update the path/filename
firebase_admin.initialize_app(cred)
db = firestore.client()

def verify_correct_database():
    try:
        # Get current project info
        app = firebase_admin.get_app()
        project_id = app.project_id
        print(f"🔗 Connected to project: {project_id}")
        
        # Test write with timestamp
        from datetime import datetime
        test_ref = db.collection("verification").document("test")
        test_data = {
            "timestamp": datetime.now().isoformat(),
            "project": project_id,
            "message": "Testing correct database connection"
        }
        test_ref.set(test_data)
        print("✅ Test write successful")
        
        # Check if any stocks data exists
        stocks_ref = db.collection("stocks")
        docs = list(stocks_ref.limit(5).stream())
        
        if docs:
            print(f"📊 Found {len(docs)} stock documents (showing first 5):")
            for doc in docs:
                print(f"  - {doc.id}: {len(doc.to_dict().get('recent_days', []))} days")
        else:
            print("📭 No stock documents found yet")
            
        # Count total stocks
        all_docs = list(stocks_ref.stream())
        print(f"📈 Total stocks in database: {len(all_docs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_last_n_trading_days(symbol, n_days=5):
    from pandas import to_datetime

    end_date = date.today()
    start_date = end_date - relativedelta(months=2)
    data = safe_get_psx_data(symbol, start_date, end_date)
    if data.empty:
        print(f"No data for {symbol} in the last two months.")
        return data
    data = data.sort_index()
    last_n = data.tail(n_days)
    return last_n

def fetch_all_stocks_last_n_days(symbols, n_days=5):
    stock_data = {}
    for symbol in symbols:
        data = get_last_n_trading_days(symbol, n_days)
        if not data.empty:
            stock_data[symbol] = data
            print(f"Fetched last {n_days} trading days for {symbol}")
        else:
            print(f"No data for {symbol}")
    return stock_data

def store_all_stocks_last_n_days_to_firebase(all_stocks_data):
    for symbol, df in all_stocks_data.items():
        records = df.reset_index().to_dict(orient="records")
        db.collection("stocks").document(symbol).set({"recent_days": records})
        print(f"Stored {symbol} last 5 days in Firebase.")

def get_all_stocks_from_firebase():
    stocks_ref = db.collection("stocks")
    docs = stocks_ref.stream()
    stocks_data = {}
    for doc in docs:
        stocks_data[doc.id] = doc.to_dict().get("recent_days", [])
    return stocks_data

def get_gainers_losers(stocks_data):
    gainers = []
    losers = []
    for symbol, days in stocks_data.items():
        if len(days) >= 2:
            prev_close = days[-2]['Close']
            last_close = days[-1]['Close']
            change_pct = ((last_close - prev_close) / prev_close) * 100 if prev_close else 0
            entry = {
                "symbol": symbol,
                "last_close": last_close,
                "change_pct": change_pct
            }
            if change_pct > 0:
                gainers.append(entry)
            elif change_pct < 0:
                losers.append(entry)
    # Sort by change_pct
    gainers = sorted(gainers, key=lambda x: x['change_pct'], reverse=True)
    losers = sorted(losers, key=lambda x: x['change_pct'])
    return gainers, losers

def load_symbols_from_file(filepath="d:/stock_genie/psx_symbols.txt"):
    with open(filepath, "r") as f:
        symbols = [line.strip() for line in f if line.strip()]
    return symbols

def safe_get_psx_data(symbol, start_date, end_date, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return data_reader.stocks(symbol, start_date, end_date)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {symbol}: {e}. Retrying ({attempt+1}/{retries})...")
            time.sleep(delay)
    print(f"Failed to fetch data for {symbol} after {retries} attempts.")
    return pd.DataFrame()

def update_stock_recent_days(symbol):
    # Fetch only the latest day
    today = date.today()
    yesterday = today - timedelta(days=7)  # Use 7 to ensure you get the last trading day (adjust as needed)
    df = safe_get_psx_data(symbol, yesterday, today)
    if df.empty:
        print(f"No new data for {symbol}")
        return

    # Get the latest day's data
    latest_row = df.sort_index().iloc[-1]
    new_day_data = latest_row.to_dict()
    new_day_data['Date'] = str(latest_row.name)  # Ensure date is serializable

    # Fetch existing recent_days from Firestore
    doc_ref = db.collection("stocks").document(symbol)
    doc = doc_ref.get()
    if doc.exists:
        recent_days = doc.to_dict().get("recent_days", [])
    else:
        recent_days = []

    # Check if this date is already present (avoid duplicates)
    if any(day.get("Date") == new_day_data["Date"] for day in recent_days):
        print(f"Data for {symbol} on {new_day_data['Date']} already exists.")
        return

    # Append and trim to last 5 days
    recent_days.append(new_day_data)
    if len(recent_days) > 5:
        recent_days = recent_days[-5:]

    doc_ref.set({"recent_days": recent_days})
    print(f"Updated {symbol} with latest day. Total days stored: {len(recent_days)}")

# Example usage:
if __name__ == "__main__":
    # symbols = load_symbols_from_file()
    # all_stocks_data = fetch_all_stocks_last_n_days(symbols, n_days=5)

    # # Print the data for each symbol
    # for symbol, df in all_stocks_data.items():
    #     print(f"\nData for {symbol}:\n{df}\n")

    # store_all_stocks_last_n_days_to_firebase(all_stocks_data)

    # After storing to Firebase, fetch and process for gainers/losers
    # stocks_data = get_all_stocks_from_firebase()
    # gainers, losers = get_gainers_losers(stocks_data)
    # print("Top Gainers:", gainers)
    # print("Top Losers:", losers)

    symbols = load_symbols_from_file()
    all_stocks_data = fetch_all_stocks_last_n_days(symbols, n_days=5)
    store_all_stocks_last_n_days_to_firebase(all_stocks_data)
    print("Done fetching and storing all PSX stocks!")
    
    #  # After storing to Firebase, fetch and process for gainers/losers
    stocks_data = get_all_stocks_from_firebase()
    gainers, losers = get_gainers_losers(stocks_data)
    print("Top Gainers:", gainers[:3])
    print("Top Losers:", losers[:3])

    # print("🔍 Verifying database connection...")
    # verify_correct_database()

    # symbols = load_symbols_from_file()
    # for symbol in symbols:
    #     update_stock_recent_days(symbol)
    # print("All stocks updated with latest day!")
<<<<<<< HEAD
import requests

def fetch_all_psx_stock_symbols():
    url = "https://dps.psx.com.pk/symbols"
    response = requests.get(url)
    data = response.json()
    # Only keep symbols that are not debt or ETF instruments
    symbols = [item['symbol'] for item in data if not item.get('isDebt') and not item.get('isETF')]
    return symbols

def save_symbols_to_file(symbols, filepath="d:/stock_genie/psx_symbols.txt"):
    with open(filepath, "w") as f:
        for symbol in symbols:
            f.write(symbol + "\n")

if __name__ == "__main__":
    symbols = fetch_all_psx_stock_symbols()
    save_symbols_to_file(symbols)
=======
import requests

def fetch_all_psx_stock_symbols():
    url = "https://dps.psx.com.pk/symbols"
    response = requests.get(url)
    data = response.json()
    # Only keep symbols that are not debt or ETF instruments
    symbols = [item['symbol'] for item in data if not item.get('isDebt') and not item.get('isETF')]
    return symbols

def save_symbols_to_file(symbols, filepath="d:/stock_genie/psx_symbols.txt"):
    with open(filepath, "w") as f:
        for symbol in symbols:
            f.write(symbol + "\n")

if __name__ == "__main__":
    symbols = fetch_all_psx_stock_symbols()
    save_symbols_to_file(symbols)
>>>>>>> bebaccb05e908cf9d30bb1ef34da0b2920fd595b
    print(f"Saved {len(symbols)} symbols to psx_symbols.txt")
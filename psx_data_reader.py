from concurrent.futures import ThreadPoolExecutor, as_completed
from dateutil.relativedelta import relativedelta
from pandas import DataFrame as container
from bs4 import BeautifulSoup as parser
from collections import defaultdict
from datetime import datetime, date
from typing import Union
import threading
import pandas as pd
import numpy as np
import requests

def moving_average(data, window=30):
    return data['Close'].rolling(window=window).mean()

def rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

class DataReader:
    headers = ['TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']

    def __init__(self):
        self.__history = "https://dps.psx.com.pk/historical"
        self.__symbols = "https://dps.psx.com.pk/symbols"
        self.__local = threading.local()

    @property
    def session(self):
        if not hasattr(self.__local, "session"):
            self.__local.session = requests.Session()
        return self.__local.session

    def get_psx_data(self, symbol: str, dates: list) -> container:
        data = []
        futures = []
        for date_ in dates:
            futures.append(ThreadPoolExecutor(max_workers=6).submit(self.download, symbol=symbol, date=date_))
        for future in as_completed(futures):
            data.append(future.result())
        data = [instance for instance in data if isinstance(instance, container)]
        return self.preprocess(data)

    def stocks(self, tickers: Union[str, list], start: date, end: date) -> container:
        tickers = [tickers] if isinstance(tickers, str) else tickers
        dates = self.daterange(start, end)
        data = [self.get_psx_data(ticker, dates)[start: end] for ticker in tickers]
        if len(data) == 1:
            return data[0]
        return pd.concat(data, keys=tickers, names=["Ticker", "Date"])

    def download(self, symbol: str, date: date):
        session = self.session
        post = {"month": date.month, "year": date.year, "symbol": symbol}
        with session.post(self.__history, data=post) as response:
            data = parser(response.text, features="html.parser")
            data = self.toframe(data)
        return data

    def toframe(self, data):
        stocks = defaultdict(list)
        rows = data.select("tr")
        for row in rows:
            cols = [col.getText() for col in row.select("td")]
            for key, value in zip(self.headers, cols):
                if key == "TIME":
                    value = datetime.strptime(value, "%b %d, %Y")
                stocks[key].append(value)
        return pd.DataFrame(stocks, columns=self.headers).set_index("TIME")

    def daterange(self, start: date, end: date) -> list:
        period = end - start
        number_of_months = period.days // 30
        current_date = datetime(start.year, start.month, 1)
        dates = [current_date]
        for month in range(number_of_months):
            prev_date = dates[-1]
            dates.append(prev_date + relativedelta(months=1))
        return dates if len(dates) else [start]

    def preprocess(self, data: list) -> pd.DataFrame:
        data = pd.concat(data)
        data = data.sort_index()
        data = data.rename(columns=str.title)
        data.index.name = "Date"
        data.Volume = data.Volume.str.replace(",", "")
        for column in data.columns:
            data[column] = data[column].str.replace(",", "").astype(np.float64)
        if 'Close' in data.columns:
            data['SMA_30'] = moving_average(data)
            data['RSI'] = rsi(data)
            data['Price_Change_Pct'] = data['Close'].pct_change()
        else:
            print("Error: 'Close' column not found in the data.")
        data.dropna(inplace=True)
        return data

# Create a single instance for import
data_reader = DataReader()
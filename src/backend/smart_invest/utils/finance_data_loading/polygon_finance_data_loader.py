from decouple import config
from polygon import RESTClient
from pandas import DataFrame, to_datetime
import datetime
import json

from .. import settings
from ..finance_data_loading import files_loading_tools as tools


class PolygonFinanceDataLoader:
    def __init__(self, top_tickers=None, data_directory=None):
        self.client = RESTClient(config("POLYGON_API_KEY"))

        if top_tickers is None:
            with open(settings.TOP_TICKERS_PATH, 'r') as tickers_file:
                self.top_tickers = json.loads(tickers_file.read())
        else:
            self.top_tickers = top_tickers

        if data_directory is None:
            self.data_directory = settings.FINANCE_DATA_DIRECTORY
        else:
            self.data_directory = data_directory

    def load_ticker_data(self,sector, ticker, start_date, end_date):
        aggs = []
        for a in self.client.list_aggs(
                ticker,
                1,
                "day",
                start_date,
                end_date,
                limit=50000,
        ):
            aggs.append(a)

        data = DataFrame(
            data=[[agg.open, agg.close, agg.high, agg.low,
                   datetime.datetime.fromtimestamp(int(agg.timestamp) / 1000.0)] for agg in aggs],
            columns=['open', 'close', 'high', 'low', 'date']
        )

        filename = f'{self.data_directory}\\{sector}\\{ticker}\\history.csv'
        tools.create_or_append_csv(data, filename)

    def download_tickers_history(self, start_date, end_date):
        for cur_sector in self.top_tickers:
            for cur_ticker in self.top_tickers[cur_sector]:
                self.load_ticker_data(cur_sector, cur_ticker, start_date, end_date)

    def load_daily_ticker_quotes(self, sector, ticker, date=None):
        if date is None:
            date = datetime.date.today()
        try:
            daily_quotes = self.client.get_daily_open_close_agg(
                ticker,
                date,
            )

            quotes_data = DataFrame(
                data=[[daily_quotes.open, daily_quotes.close, daily_quotes.high, daily_quotes.low, date]],
                columns=['open', 'close', 'high', 'low', 'date']
            )
            filename = f'{self.data_directory}\\{sector}\\{ticker}\\history.csv'
            tools.create_or_append_csv(quotes_data, filename)

        except Exception as exeption:
            pass

    def load_daily_tickers_quotes(self, date=None):
        if date is None:
            date = datetime.date.today()

        for cur_sector in self.top_tickers:
            for cur_ticker in self.top_tickers[cur_sector]:
                self.load_daily_ticker_quotes(cur_sector, cur_ticker,  to_datetime(date))


class PolygonFinanceDataLoader1:
    def __init__(self, top_tickers=None, data_directory=None):
        self.client = RESTClient("R3zkQ7o0De4xXphOseKSqy2XRGW6kauq")

        if top_tickers is None:
            with open(settings.TOP_TICKERS_PATH, 'r') as tickers_file:
                self.top_tickers = json.loads(tickers_file.read())
        else:
            self.top_tickers = top_tickers

        if data_directory is None:
            self.data_directory = settings.FINANCE_DATA_DIRECTORY
        else:
            self.data_directory = data_directory

    def load_ticker_history(self, sector, ticker, start_date, end_date):
        aggs = []
        for a in self.client.list_aggs(
                ticker,
                1,
                "day",
                start_date,
                end_date,
                limit=50000,
        ):
            aggs.append(a)

        data = DataFrame(
            data=[[agg.open, agg.close, agg.high, agg.low,
                   datetime.datetime.fromtimestamp(int(agg.timestamp) / 1000.0)] for agg in aggs],
            columns=['open', 'close', 'high', 'low', 'date']
        )

        filename = f'{self.data_directory}\\{sector}\\{ticker}\\history.csv'
        tools.create_or_append_csv(data, filename)

    def load_tickers_history(self, start_date, end_date):
        for cur_sector in self.top_tickers:
            for cur_ticker in self.top_tickers[cur_sector]:
                self.load_ticker_history(cur_sector, cur_ticker, start_date, end_date)

    def load_daily_ticker_quotes(self, sector, ticker, date=None):
        if date is None:
            date = datetime.date.today()
        try:
            daily_quotes = self.client.get_daily_open_close_agg(
                ticker,
                date,
            )

            quotes_data = DataFrame(
                data=[[daily_quotes.open, daily_quotes.close, daily_quotes.high, daily_quotes.low, date]],
                columns=['open', 'close', 'high', 'low', 'date']
            )
            filename = f'{self.data_directory}\\{sector}\\{ticker}\\history.csv'
            tools.create_or_append_csv(quotes_data, filename)

        except Exception as exeption:
            pass

    def load_daily_tickers_quotes(self, date=None):
        if date is None:
            date = datetime.date.today()

        for cur_sector in self.top_tickers:
            for cur_ticker in self.top_tickers[cur_sector][:2]:
                self.load_daily_ticker_quotes(cur_sector, cur_ticker, date)






import bt
import pandas as pd
from pandas import DataFrame, read_csv
from numpy import array
import datetime

from ... import settings


class WeighTarget(bt.Algo):
    """
    Sets target weights based on a target weight DataFrame.
    Args:
        * target_weights (DataFrame): DataFrame containing the target weights
    Sets:
        * weights
    """

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.portfolio['creation_date'] = pd.to_datetime(self.portfolio['creation_date']).dt.tz_localize(None)
        self.change_dates = pd.to_datetime(portfolio['creation_date']).dt.tz_localize(None).unique()

    def __call__(self, target):
        # get target weights on date target.now
        if target.now in self.change_dates:
            # print('now')
            tickers_to_change = self.portfolio[self.portfolio['creation_date'] == target.now]
            # print(tickers_to_change.shape)

            # save in temp - this will be used by the weighing algo
            target.temp['selected'] = tickers_to_change.stock_name.unique().tolist()

            # save in temp - this will be used by the weighing algo
            # also dropping any na's just in case they pop up
            target.temp['weights'] = {ticker: weight for (ticker, weight) in
                                      tickers_to_change.loc[:, ('stock_name', 'part')].values}

            # return True because we want to keep on moving down the stack
            return True
        return False


class PortfoliosTester:
    def __init__(self, portfolios=None):
        self.portfolios = portfolios

    def load_portfolio_tickers_data(self, portfolio):
        yf_data_directory = settings.FINANCE_DATA_DIRECTORY
        start_date = portfolio.creation_date.min().tz_localize(None)
        tickers = list(set([(sector, symbol) for sector, symbol in portfolio[['sector', 'stock_name']].values]))
        portfolio_data = []
        ticker_names = []
        dates = None
        for (sector, ticker) in tickers:
            history_path = f'{yf_data_directory}\\{sector}\\{ticker}\\history.csv'
            history = read_csv(history_path, parse_dates=['date'])
            history = history[history['date'] >= start_date]
            if dates is None:
                dates = history['date']
            portfolio_data.append(history['close'].values)
            ticker_names.append(ticker)

        return DataFrame(data=array(portfolio_data).T, columns=ticker_names, index=dates)

    def long_only_ew(self, tickers, start='2019-01-01', name='long_only_ew'):
        s = bt.Strategy(name, [bt.algos.RunOnce(),
                               bt.algos.SelectAll(),
                               bt.algos.WeighEqually(),
                               bt.algos.Rebalance()])
        if name.lower() == 'spy':
            data = pd.read_csv(settings.MARKET_DATA_PATH, parse_dates=['date']) \
                .set_index('date').rename(columns={'low': 'SPY'})
        else:
            data = bt.get(tickers, start=start)
        return bt.Backtest(s, data)

    def create_backtest(self, benchmark=None):
        backtests = []
        # min_date = datetime.datetime.now()
        for strategy_name, portfolio in self.portfolios.items():
            min_date = portfolio.creation_date.min()
            portfolio_data = self.load_portfolio_tickers_data(portfolio)
            strategy = bt.Strategy(strategy_name,
                                   [WeighTarget(portfolio),
                                    bt.algos.Rebalance()])
            backtest = bt.Backtest(strategy, portfolio_data)
            backtests.append(backtest)

        if isinstance(benchmark, str):
            benchmark = self.long_only_ew(benchmark, start=min_date, name=benchmark)
            backtests.append(benchmark)
        elif isinstance(benchmark, list):
            for ticker in benchmark:
                ticker_benchmark = self.long_only_ew(ticker, start='2019-01-01', name=ticker)
                backtests.append(ticker_benchmark)
        return backtests


# class PortfoliosTester:
#     def __init__(self, portfolios=None):
#         self.portfolios = portfolios
#
#     def load_portfolio_tickers_data(self, portfolio):
#         yf_data_directory = settings.FINANCE_DATA_DIRECTORY
#         start_date = portfolio.creation_date.min()
#         tickers = list(set([(sector, symbol) for sector, symbol in portfolio[['sector', 'symbol']].values]))
#         portfolio_data = []
#         ticker_names = []
#         dates = None
#         for (sector, ticker) in tickers:
#             history_path = f'{yf_data_directory}\\{sector}\\{ticker}\\history.csv'
#             history = read_csv(history_path, parse_dates=['date'])
#             history = history[history['date'] >= start_date]
#             if dates is None:
#                 dates = history['date']
#             portfolio_data.append(history['close'].values)
#             ticker_names.append(ticker)
#
#         return DataFrame(data=array(portfolio_data).T, columns=ticker_names, index=dates)
#
#     def long_only_ew(self, tickers, start='2021-01-01', name='long_only_ew'):
#         s = bt.Strategy(name, [bt.algos.RunOnce(),
#                                bt.algos.SelectAll(),
#                                bt.algos.WeighEqually(),
#                                bt.algos.Rebalance()])
#         data = bt.get(tickers, start=start)
#         return bt.Backtest(s, data)
#
#     def create_backtest(self, benchmark=None):
#         backtests = []
#         min_date = datetime.datetime.now()
#         for strategy_name, portfolio in self.portfolios.items():
#             min_date = min(min_date, portfolio.creation_date.min())
#             portfolio_data = self.load_portfolio_tickers_data(portfolio)
#             strategy = bt.Strategy(strategy_name,
#                                    [WeighTarget(portfolio),
#                                     bt.algos.Rebalance()])
#             backtest = bt.Backtest(strategy, portfolio_data)
#             backtests.append(backtest)
#
#         if isinstance(benchmark, str):
#             benchmark = self.long_only_ew(benchmark, start=min_date, name=benchmark)
#             backtests.append(benchmark)
#         elif isinstance(benchmark, list):
#             for ticker in benchmark:
#                 ticker_benchmark = self.long_only_ew(ticker, start=min_date, name=ticker)
#                 backtests.append(ticker_benchmark)
#         return backtests


# class PortfoliosTester1:
#     def __init__(self, portfolios=None):
#         self.portfolios = portfolios
#
#     def load_portfolio_tickers_data(self, portfolio, history_directory=None):
#         if history_directory is None:
#             history_directory = src.setings.YF_DATA_DIRECTORY
#         start_date = portfolio.creation_date.min()
#         tickers = list(set([(sector, symbol) for sector, symbol in portfolio[['sector', 'symbol']].values]))
#         portfolio_data = []
#         ticker_names = []
#         dates = None
#         for (sector, ticker) in tickers:
#             history_path = f'{history_directory}\\{sector}\\{ticker}\\history.csv'
#             history = read_csv(history_path, parse_dates=['Date'])
#             history = history[history['date'] >= start_date]
#             if dates is None:
#                 dates = history['date']
#             portfolio_data.append(history['close'].values)
#             ticker_names.append(ticker)
#
#         return DataFrame(data=array(portfolio_data).T, columns=ticker_names, index=dates)
#
#     def long_only_ew(self, tickers, start='2019-01-01', name='long_only_ew'):
#         s = bt.Strategy(name, [bt.algos.RunOnce(),
#                                bt.algos.SelectAll(),
#                                bt.algos.WeighEqually(),
#                                bt.algos.Rebalance()])
#         data = bt.get(tickers, start=start)
#         return bt.Backtest(s, data)
#
#     def create_backtest(self, benchmark=None):
#         backtests = []
#         min_date = datetime.datetime.now()
#         for strategy_name, portfolio in self.portfolios.items():
#             min_date = min(min_date, portfolio.creation_date.min())
#             portfolio_data = self.load_portfolio_tickers_data(portfolio)
#             strategy = bt.Strategy(strategy_name,
#                                    [WeighTarget(portfolio),
#                                     bt.algos.Rebalance()])
#             backtest = bt.Backtest(strategy, portfolio_data)
#             backtests.append(backtest)
#
#         if isinstance(benchmark, str):
#             benchmark = self.long_only_ew(benchmark, start=min_date, name=benchmark)
#             backtests.append(benchmark)
#         elif isinstance(benchmark, list):
#             for ticker in benchmark:
#                 ticker_benchmark = self.long_only_ew(ticker, start=min_date, name=ticker)
#                 backtests.append(ticker_benchmark)
#         return backtests
#
#     def test(self, benchmark='spy'):
#         backtest = self.create_backtest(benchmark=benchmark)
#         res = bt.run(*backtest)
#         return res
import datetime
import bt
import pandas as pd
from pandas import DataFrame, read_csv
from numpy import concatenate
import json
from polygon import RESTClient

from ... import settings
from ...finance_data_loading import files_loading_tools as tools
from ...finance_data_loading import PolygonFinanceDataLoader, YahooFinanceDownloader
from .backtest import PortfoliosTester
from main_app.models import PortfolioComposition, Strategy


class StatUpdater:

    def __init__(self):
        # self.finance_data_loader = PolygonFinanceDataLoader()
        self.finance_data_loader = YahooFinanceDownloader()
        self.client = RESTClient("R3zkQ7o0De4xXphOseKSqy2XRGW6kauq")

    def update_tickers_quotes(self, period='5d', interval='1d'):
        self.finance_data_loader.download_tickers_history(period=period, interval=interval)

    def update_market_data(self, start_date=None):
        if start_date is None:
            start_date = str(datetime.date.today() - datetime.timedelta(10))
        end_date = str(datetime.date.today())
        aggs = []
        for a in self.client.list_aggs(
                "SPY",
                1,
                "day",
                start_date,
                end_date,
                limit=50000,
        ):
            aggs.append(a)

        market_data = pd.DataFrame(
            data=[[agg.open, agg.close, agg.high, agg.low,
                   datetime.date.fromtimestamp(int(agg.timestamp) / 1000.0)] for agg in aggs],
            columns=['open', 'close', 'high', 'low', 'date']
        )
        market_data['date'] = pd.to_datetime(market_data['date'])
        tools.create_or_append_csv(market_data, settings.MARKET_DATA_PATH,
                                   cols_to_concat=['open', 'close', 'high', 'low', 'date'])

        return market_data

    def update_incorrect_rated_shares(self, topn=5, save=True):
        with open(settings.TOP_TICKERS_PATH, 'r') as top_tickers_file:
            top_tickers = json.loads(top_tickers_file.read())

        shares_comparison = []

        for sector, tickers in top_tickers.items():
            for ticker in tickers:
                ticker_directory = f'{settings.FINANCE_DATA_DIRECTORY}\\{sector}\\{ticker}'
                try:
                    history = read_csv(f'{ticker_directory}\\history.csv', parse_dates=['date'])
                    fair_history = read_csv(f'{ticker_directory}\\fair_history.csv', parse_dates=['date'])
                    # print('history files was read')
                    last_actual_quote = history.sort_values(by='date', ascending=False)['close'].values[0]
                    last_fair_quote = fair_history.dropna().sort_values(by='date', ascending=False)['fair_market_cap_norm'].values[0]
                    shares_comparison.append([ticker, last_actual_quote, last_fair_quote])
                except:
                    pass
        shares_comparison = DataFrame(columns=['symbol', 'last_actual_quote', 'last_fair_quote'],
                                         data=shares_comparison)
        # print(shares_comparison.shape)
        shares_comparison['fair_real_ratio'] = shares_comparison['last_fair_quote'] / shares_comparison['last_actual_quote']

        overrated_shares = shares_comparison[shares_comparison['fair_real_ratio'] < 1] \
            .sort_values(by='fair_real_ratio', ascending=True).head(topn)

        underrated_shares = shares_comparison[shares_comparison['fair_real_ratio'] > 1] \
            .sort_values(by='fair_real_ratio', ascending=False).head(topn)

        if save:
            overrated_shares.to_csv(settings.QUOTES_DIRECTORY + '\\overrated_shares.csv', index=False)
            underrated_shares.to_csv(settings.QUOTES_DIRECTORY + '\\underrated_shares.csv', index=False)

        return overrated_shares, underrated_shares

    def update_main_tickers_quotes(self):
        actual_quotes = []

        with open(settings.MAIN_TICKERS_PATH, 'r') as main_tickers_file:
            main_tickers = json.loads(main_tickers_file.read())

        for ticker, sector, name in main_tickers:
            ticker_directory = f'{settings.FINANCE_DATA_DIRECTORY}\\{sector}\\{ticker}'
            history = read_csv(f'{ticker_directory}\\history.csv', parse_dates=['date'])
            last_quotes = history.sort_values(by='date', ascending=False).iloc[:2]
            quote_summary = concatenate([
                [name],
                last_quotes.iloc[1][['close', 'high', 'low', 'date']].values,
                [last_quotes.close.diff(-1).values[0]],
                [round(last_quotes.close.diff(-1).values[0] / last_quotes.close.values[0] * 100, 2)],
            ])
            actual_quotes.append(quote_summary)

        actual_quotes = DataFrame(actual_quotes,
                                  columns=['name', 'last', 'max', 'min', 'date', 'change', 'relative_change'])
        actual_quotes.to_csv(settings.QUOTES_DIRECTORY + '\\main_tickers_quotes.csv', index=False)
        return actual_quotes

    def update_strategy_stats(self):
        portfolios = {}
        for strategy_id in Strategy.objects.all().values_list('id'):
            strategy_portfolios = PortfolioComposition.objects.filter(strategy_id=strategy_id).values()
            strategy_portfolios = DataFrame(list(strategy_portfolios))
            strategy_portfolios['creation_date'] = pd.to_datetime(strategy_portfolios['creation_date'])
            portfolios[f'strategy_{strategy_id[0]}'] = strategy_portfolios

        portfolio_tester = PortfoliosTester(portfolios)
        backtests = portfolio_tester.create_backtest(benchmark='spy')

        res = bt.run(*backtests)

        res.prices.reset_index().rename(columns={'index': 'date'}).\
            to_csv(settings.STRATEGIES_DIRECTORY + '\\strategies_prices.csv', index=False)

        res.stats.T.loc[:, ('start', 'end', 'total_return', 'max_drawdown', 'daily_sharpe', 'daily_sortino',
                            'daily_mean', 'monthly_sharpe', 'monthly_sortino', 'monthly_mean', 'avg_drawdown')]. \
            reset_index().rename(columns={'index': 'strategy'}).\
            to_csv(settings.STRATEGIES_DIRECTORY + '\\strategies_stats.csv', index=False)

    def update(self):
        print('Updating starting')
        self.update_tickers_quotes(period='1mo')
        print('update market data')
        self.update_market_data(start_date='2023-01-01')
        print('Tickers quotes updated')
        self.update_incorrect_rated_shares()
        print('Incorrect rates quotes updated')
        self.update_main_tickers_quotes()
        print('Main tickers updated')
        self.update_strategy_stats()
        print('Strategy stats updated')

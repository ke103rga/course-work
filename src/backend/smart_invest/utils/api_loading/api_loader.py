from django.http import JsonResponse
from main_app.models import News, PortfolioComposition
from pandas import read_csv, Series, to_datetime
import json

from .. import settings


class ApiLoader:
    def __init__(self):
        with open(settings.FINANCE_DATA_DIRECTORY + '\\ticker_to_sector.json', 'r') as tickers_file:
            self.ticker_to_sector = json.loads(tickers_file.read())

    @staticmethod
    def get_prices_in_percents(prices: Series):
        prices = prices.copy()
        first_price = prices[0]
        prices = prices.apply(lambda price: price / first_price * 100)
        return prices

    def load_news(self, limit=100):
        values_list = ['title', 'author', 'article_url', 'image_url', 'description', 'published_utc', 'publisher_name']
        news = News.objects.order_by('published_utc')[:limit].values(*values_list)
        json_result = {
            'news': list(news)
        }
        return json_result

    def load_main_tickers_data(self):
        main_tickers_data = read_csv(settings.QUOTES_DIRECTORY + '\\main_tickers_quotes.csv')
        main_tickers_data['date'] = to_datetime(main_tickers_data['date']).dt.strftime('%d.%m.%Y')
        main_tickers_data_json = main_tickers_data.to_json(orient='index')
        json_result = {
            'main_tickers_data': main_tickers_data_json
        }
        return json_result

    def load_incorrect_rated_shares(self):
        overrated_shares = read_csv(settings.QUOTES_DIRECTORY + '\\overrated_shares.csv')
        underrated_shares = read_csv(settings.QUOTES_DIRECTORY + '\\underrated_shares.csv')
        overrated_shares_json = overrated_shares.to_json(orient='index')
        underrated_shares_json = underrated_shares.to_json(orient='index')
        json_result = {
            'overrated_shares': overrated_shares_json,
            'underrated_shares': underrated_shares_json
        }
        return json_result

    def load_ticker_history(self, ticker):
        ticker = ticker.upper()
        sector = self.ticker_to_sector.get(ticker, 0)
        if sector == 0:
            return JsonResponse({'message': 'Ticker with such name does not exists'})
        ticker_directory = f'{settings.FINANCE_DATA_DIRECTORY}\\{sector}\\{ticker}'
        history = read_csv(f'{ticker_directory}\\history.csv', parse_dates=['date'])
        history = history.loc[:, ('date', 'close')]
        fair_history = read_csv(f'{ticker_directory}\\fair_history.csv', parse_dates=['date'])
        fair_history = fair_history.loc[:, ('date', 'fair_market_cap_norm')]\
            .rename(columns={'fair_market_cap_norm': 'fair_cost'})
        history_json = history.to_json(orient='index')
        if fair_history.shape[0] == 0 or history.shape[0] == 0:
            return JsonResponse({'message': 'No info about that ticker'})
        fair_history_json = fair_history.to_json(orient='index')
        json_result = {
            'history': history_json,
            'fair_history': fair_history_json
        }
        return json_result

    def load_strategies_info(self, strategy_id=1):
        strategy_prices = read_csv(settings.STRATEGIES_DIRECTORY + '\\strategies_prices.csv')
        strategy_stats = read_csv(settings.STRATEGIES_DIRECTORY + '\\strategies_stats.csv')
        for price_col in strategy_prices.drop(columns=['date']).columns:
            strategy_prices[price_col] = ApiLoader.get_prices_in_percents(strategy_prices[price_col])

        cols_to_round = ['total_return', 'max_drawdown', 'daily_sharpe', 'daily_sortino',
                         'daily_mean', 'monthly_sharpe', 'monthly_sortino', 'monthly_mean', 'avg_drawdown']

        for col_to_round in cols_to_round:
            strategy_stats[col_to_round] = strategy_stats[col_to_round].round(4)

        strategy_prices_json = strategy_prices.to_json(orient='index')
        strategy_stats_json = strategy_stats.to_json(orient='index')
        json_result = {
            'strategy_prices': strategy_prices_json,
            'strategy_stats': strategy_stats_json
        }
        return json_result

    def load_actual_portfolio(self, strategy_id=1):
        last_updating_date = PortfolioComposition.objects.order_by('-creation_date')[0].creation_date
        values_list = ['sector', 'stock_name', 'part']
        actual_portfolio = PortfolioComposition.objects.filter(creation_date=last_updating_date)\
            .values(*values_list)
        actual_portfolio = actual_portfolio.exclude(part=0)
        json_result = {
            'actual_portfolio': list(actual_portfolio)
        }
        return json_result


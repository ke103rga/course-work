import pandas as pd
import datetime

from main_app.models import Strategy, PortfolioComposition
from ...finance_data_loading.yahoo_finance_data_loader import YahooFinanceDownloader
from .dataframe_building.dataframe_builder import DataFrameBuilder
from .data_preprocessors import ToNumDataPreprocessor, ToNumAndCatDataPreprocessor
from .portfolio_rebalancer import PortfolioBalancer
from .fair_rates_predicting.blending_ensemble_predictor import BlendingEnsemble


class PortfolioUpdater:
    def __init__(self):
        self.finance_downloader = YahooFinanceDownloader()
        self.df_builder = DataFrameBuilder()

        self.to_num_preprocessor = ToNumDataPreprocessor()
        self.to_num_and_cat_preprocessor = ToNumAndCatDataPreprocessor()

    def preprocess_data(self, reports_data, cols_to_ignore=['date', 'target']):
        num_data = self.to_num_preprocessor.transform(reports_data, cols_to_ignore=cols_to_ignore)
        cat_data = self.to_num_and_cat_preprocessor.transform(reports_data, cols_to_ignore=cols_to_ignore)
        return num_data.drop(columns=cols_to_ignore), cat_data.drop(columns=cols_to_ignore), reports_data

    def get_actual_strategy_portfolio(self, strategy_id):
        last_updating_date = PortfolioComposition.objects.filter(pk=strategy_id)\
            .order_by('-creation_date')[0].creation_date
        actual_portfolio = PortfolioComposition.objects.filter(creation_date=last_updating_date)
        actual_portfolio = actual_portfolio.exclude(part=0)
        if actual_portfolio is not None:
            actual_portfolio = pd.DataFrame.from_records(actual_portfolio.all().values())
            return actual_portfolio
        return None

    def update(self):
        strategies = Strategy.objects.all()
        for strategy in strategies:
            df_builder = DataFrameBuilder(features=strategy.features, market_cap_n_days=strategy.target_n_days)
            data = df_builder.build_common_df()
            num_data = strategy.to_num_preprocessor.transform(data, cols_to_ignore=[])
            num_cat_data = strategy.to_num_and_cat_preprocessor.transform(data, cols_to_ignore=[])

            rebalancer = PortfolioBalancer(
                strategy.predictor, data,
                strategy.tickers_from_sector,
                strategy.criterion
            )
            fr_rates = rebalancer.predict_fair_real_rates({'num_X': num_data, 'cat_X': num_cat_data}, data,
                                                               datetime.date.today())
            current_portfolio = self.get_actual_strategy_portfolio(strategy.pk)
            new_portfolio = rebalancer.update_portfolio(fr_rates, current_portfolio)
            portfolio_changes = rebalancer.calculate_portfolio_changes(new_portfolio, current_portfolio)
            portfolio_changes['change_date'] = pd.to_datetime(datetime.date.today())

            full_portfolio_composition = pd.concat([
                current_portfolio, portfolio_changes
            ])
            full_portfolio_composition_records = full_portfolio_composition.to_dict('records')
            model_instances = [PortfolioComposition(
                field_1=record['field_1'],
                field_2=record['field_2'],
            ) for record in full_portfolio_composition_records]

            PortfolioComposition.objects.bulk_create(model_instances)


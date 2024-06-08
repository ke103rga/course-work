from main_app.models import Strategy
from ...finance_data_loading.yahoo_finance_data_loader import YahooFinanceDownloader
from .dataframe_building.dataframe_builder import DataFrameBuilder
from .data_preprocessors import ToNumDataPreprocessor, ToNumAndCatDataPreprocessor


class PortfolioUpdater:
    def __init__(self):
        self.finance_downloader = YahooFinanceDownloader()
        self.df_builder = DataFrameBuilder()

        self.to_num_preprocessor = ToNumDataPreprocessor()
        self.to_num_and_cat_preprocessor = ToNumAndCatDataPreprocessor()

    def update_portfolios(self):
        strategies = Strategy.objects.all()
        for strategy in strategies:
            df_builder = DataFrameBuilder(features=strategy.features, market_cap_n_days=strategy.target_n_days)
            data = df_builder.build_common_df()
            num_data = strategy.to_num_preprocessor.transform(data, cols_to_ignore=[])
            num_cat_data = strategy.to_num_and_cat_preprocessor.transform(data, cols_to_ignore=[])

        self.finance_downloader.download_top_tickers_data()
        self.df_builder.build_common_df()

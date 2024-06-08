import pandas as pd
import numpy as np
import os
import json

from .... import settings
from .features_extracting import report_features_extractor, price_history_features_extractor
pd.options.mode.chained_assignment = None


class DataFrameBuilder:

    def __init__(self, data_directory=None, tickers=None, features=None, market_data=None,
                 final_features=None, market_cap_n_days=None):
        if data_directory is None:
            self.data_directory = settings.FINANCE_DATA_DIRECTORY
        else:
            self.data_directory = data_directory

        if tickers is None:
            if os.path.exists(settings.VALID_TICKERS_PATH):
                with open(settings.TOP_TICKERS_PATH, 'r') as valid_tickers_file:
                    self.tickers = json.loads(valid_tickers_file.read())
            else:
                raise ValueError('')
        else:
            self.tickers = tickers

        if features is None:
            filepath = settings.BASE_FEATURES_PATH
            with open(filepath, 'r') as features_file:
                self.features = json.loads(features_file.read())
        else:
            self.features = features

        if final_features is None:
            filepath = settings.FINAL_FEATURES_PATH
            with open(filepath, 'r') as features_file:
                self.final_features = json.loads(features_file.read())
        else:
            self.final_features = final_features

        if market_data is None:
            filepath = settings.MARKET_DATA_PATH
            self.market_data = pd.read_csv(filepath, parse_dates=['date'])
        else:
            self.market_data = market_data

        self.reports_features_extractor = report_features_extractor.ReportsFeaturesExtractor(self.features)
        self.share_cost_features_extractor = price_history_features_extractor.PriceHistoryFeaturesExtractor(market_data)
        self.market_cap_n_days = market_cap_n_days
        # self.target_calculator = target.SmoothedQuarterlyTarget()

    @staticmethod
    def uniquify(filepath):
        filename, extension = os.path.splitext(filepath)
        counter = 1

        while os.path.exists(filepath):
            filepath = filename + " (" + str(counter) + ")" + extension
            counter += 1

        return filepath

    @staticmethod
    def select_closest_ndays(history, report_date, n=10, back=True):
        deltas = (pd.to_datetime(report_date) - pd.to_datetime(history['date'].dt.date)).apply(lambda delta: delta.days)

        if back:
            closest_history = history.loc[deltas[deltas > 0].sort_values().head(n).index, ('open', 'close', 'date')]
        else:
            closest_history = history.loc[
                deltas[deltas < 0].sort_values(ascending=False).head(n).index, ('open', 'close', 'date')]
        closest_history['day_mean'] = closest_history.loc[:, ('open', 'close')].mean(axis=1)
        return closest_history.loc[:, ('date', 'day_mean')].sort_values(by=['date'])

    def compute_market_cap(self, df, history, n_days):
        df['smoothed_share_cost'] = df.date \
            .apply(lambda date: self.select_closest_ndays(history, date, n=n_days, back=True)['day_mean'].mean())
        df['market_cap'] = df['smoothed_share_cost'] * df['ordinary_shares_number']
        return df.drop(columns=['smoothed_share_cost'])

    def build_ticker_df(self, ticker_sector, ticker_name):

        ticker_directory = f'{self.data_directory}\\{ticker_sector}\\{ticker_name}'
        # Loading current ticker data
        try:
            balance_sheet = pd.read_csv(f'{ticker_directory}\\quarterly_balance_sheet.csv', parse_dates=['date'])
            income_stmt = pd.read_csv(f'{ticker_directory}\\quarterly_income_statement.csv', parse_dates=['date'])
            cashflow = pd.read_csv(f'{ticker_directory}\\quarterly_cashflow.csv', parse_dates=['date'])
            history = pd.read_csv(f'{ticker_directory}\\history.csv', parse_dates=['date'])
            # print(balance_sheet.shape)
        except FileNotFoundError as ex:
            print(f'Ticker: {ticker_name.ljust(5)} impossible to process due to absence of data')
            return None
        # Check if every report contains at least one row
        if any([balance_sheet.shape[0] == 0, income_stmt.shape[0] == 0, cashflow.shape[0] == 0]):
            return None

        # Extract features
        df = self.reports_features_extractor.select_key_features(balance_sheet, income_stmt, cashflow)
        df = self.reports_features_extractor.add_multiplicators(df)
        df = self.share_cost_features_extractor.extraсt_history_features_per_period(df, history)
        if df is None:
            return None
        df = self.reports_features_extractor.add_diff_features(df)
        df['sector'] = ticker_sector
        df['symbol'] = ticker_name
        max_date = df['date'].max()
        df['actual'] = df['date'].apply(lambda date: date == max_date)
        # compute market capitalization
        df = self.compute_market_cap(df, history, self.market_cap_n_days)
        # print(f'Ticker: {ticker_name.ljust(5)} was successfully processed')
        return df

    def build_common_df(self, common_df_name='common_df', final_df_name='final_df'):

        common_df = None
        for sector, tickers in self.tickers.items():
            for ticker in tickers[:2]:
                ticker_df = self.build_ticker_df(sector, ticker)
                if ticker_df is None:
                    continue
                if common_df is None:
                    common_df = ticker_df
                else:
                    common_df = pd.concat([common_df, ticker_df])
        # Saving original dataframe
        common_df.to_csv(self.uniquify(f'{self.data_directory}\\{common_df_name}.csv'), index=False)

        final_df = common_df.copy()
        final_df = final_df.loc[:, self.final_features]
        final_df = final_df.dropna()

        # Saving final version of dataframe
        final_df.to_csv(self.uniquify(f'{self.data_directory}\\{final_df_name}.csv'), index=False)

        return final_df


def build_df(n_days=15):
    df_builder = DataFrameBuilder()
    df_builder.build_common_df(common_df_name=f'common_df_target_{n_days}', final_df_name=f'final_df_target_{n_days}')


if __name__ == '__main__':
    # data_directory = 'D:\\pythonProg\\PycharmProjects\\PortfolioRebalancer\\finance_data\\yahoo_finance_data'
    df_builder = DataFrameBuilder()
    df_builder.build_common_df(common_df_name='common_df_target_15', final_df_name='final_df_target_15')

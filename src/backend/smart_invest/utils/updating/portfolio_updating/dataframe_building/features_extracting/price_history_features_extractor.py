from functools import reduce
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.signal import find_peaks


class PriceHistoryFeaturesExtractor:
    def __init__(self, market_data=None, market_data_price_col='close', market_data_date_col='date'):
        # Load market data if it wasn't passed
        if market_data is None:
            spy = yf.Ticker('SPY')
            market_data = spy.history(period='3y', interval="1d")
            market_data = market_data.reset_index()
            market_data['date'] = pd.to_datetime(market_data['Date'].dt.date)
            self.market_data = market_data.rename(columns={'Close': 'close'})
            self.market_data_price_col = 'close'
            self.market_data_date_col = 'date'

        elif market_data_price_col not in market_data.columns:
            raise ValueError('market data should contains column which was passed as "market_data_price_col"')

        elif market_data_date_col not in market_data.columns:
            raise ValueError('market data should contains column which was passed as "market_data_date_col"')

        else:
            self.market_data = market_data
            self.market_data_price_col = market_data_price_col
            self.market_data_date_col = market_data_date_col


    @staticmethod
    def calculate_daily_returns(df, price_col):
        prices_diff = df[price_col].diff()
        prices_diff_shifted = prices_diff.shift(-1)
        df.loc[:, 'daily_returns'] = ((prices_diff_shifted / df[price_col]) * 100).shift(1)
        return df

    @staticmethod
    def calculate_amount_of_outliers(df):
        low = np.quantile(df, q=0.25)
        high = np.quantile(df, q=0.75)
        iqr = 1.5 * (high - low)
        low_edge = low - iqr
        high_edge = high + iqr
        return df[(df > high_edge) | (df < low_edge)].shape[0]

    @staticmethod
    def calculate_geom_mean(share_profitability, risk_free_profitability=None):
        share_profitability_mul = reduce(lambda x, y: x * (1 + y / 100), share_profitability.fillna(1))
        if risk_free_profitability is None:
            risk_free_profitability_mul = 0
        else:
            risk_free_profitability_mul = reduce(lambda x, y: x * (1 + y / 100), risk_free_profitability.fillna(1))
        return (share_profitability_mul - risk_free_profitability_mul) ** (1 / share_profitability.shape[0]) - 1

    @staticmethod
    def calculate_capm_coefs(df, data_price_col='close', data_date_col='date',
                             market_data=None, market_data_date_col='date',
                             market_data_price_col='close'):

        # Select only periods which includes information about both of tickers
        min_date = max(market_data[market_data_date_col].min(), df[data_date_col].min())
        max_date = min(market_data[market_data_date_col].max(), df[data_date_col].max())
        df = df[(df[data_date_col] >= min_date) & (df[data_date_col] <= max_date)]
        market_data = market_data[
            (market_data[market_data_date_col] >= min_date) & (market_data[market_data_date_col] <= max_date)
        ]

        # Computing daily returns
        df = PriceHistoryFeaturesExtractor.calculate_daily_returns(df, data_price_col)
        market_data = PriceHistoryFeaturesExtractor.calculate_daily_returns(market_data, market_data_price_col)

        # Computing the CAPM params
        beta, alpha = np.polyfit(market_data['daily_returns'].fillna(0), df['daily_returns'].fillna(0), deg=1)
        return beta, alpha

    def extract_history_features(self, history, start_date, end_date, agg_stats=None,
                                 date_col='date', econometric_period=2):
        if agg_stats is None:
            agg_stats = [np.mean, np.std, np.max, np.min, self.calculate_amount_of_outliers]
        history_features = {}

        # Select time period to describe econometric features
        econometric_history = history.copy()
        econometric_history = econometric_history[
            (econometric_history[date_col] >= end_date - pd.DateOffset(years=econometric_period)) &
            (econometric_history[date_col] <= end_date)
        ]

        # Select time period to describe 'visual' features for current period
        history = history[(history[date_col] >= start_date) & (history[date_col] <= end_date)]
        if history.shape[0] < 20:
            return None

        # Extract features
        history['amplitude'] = history['high'] - history['low']
        history['day_mean'] = history.loc[:, ('open', 'close')].mean(axis=1)
        history['day_mean_pct_change'] = history['day_mean'].pct_change()
        history['peaks_3_days'] = history['day_mean'].rolling(3).apply(lambda x: len(find_peaks(x)[0]))
        history['peaks_week'] = history['day_mean'].rolling(7).apply(lambda x: len(find_peaks(x)[0]))
        # Compute shares profitability
        history = self.calculate_daily_returns(history, price_col='day_mean')
        econometric_history['day_mean'] = econometric_history.loc[:, ('open', 'close')].mean(axis=1)
        econometric_history = self.calculate_daily_returns(econometric_history, price_col='day_mean')
        # Compute aggregated statistics
        for feature in ['day_mean', 'volume', 'amplitude', 'daily_returns']:
            for agg_func in agg_stats:
                history_features[f'{feature} ({agg_func.__name__})'] = agg_func(history[feature])
        history_features['amount_of_3days_peaks'] = history['peaks_3_days'].sum()
        history_features['amount_of_week_peaks'] = history['peaks_week'].sum()
        # Compute econometric params
        history_features['sharp_ratio'] = econometric_history['daily_returns'].mean() / econometric_history['day_mean'].std()
        diffs = econometric_history['daily_returns'].apply(lambda x: x - np.mean(econometric_history['daily_returns']))
        history_features['sortino_ratio'] = econometric_history['daily_returns'].mean() / diffs[diffs > 0].sum()
        history_features['geom_mean'] = self.calculate_geom_mean(econometric_history['daily_returns'])

        return history_features

    def extraсt_history_features_per_period(self, df, history, date_col='date'):
        hist_data = []
        for i in range(df.shape[0] - 1):
            start_date, end_date = df.sort_values(by=date_col, ascending=True).iloc[i:i + 2][date_col]
            features = self.extract_history_features(history, start_date, end_date)
            if features is None:
                continue
            beta, alpha = self.calculate_capm_coefs(
                df=history[history[date_col] <= end_date],
                market_data=self.market_data,
                market_data_date_col=self.market_data_date_col,
                market_data_price_col=self.market_data_price_col
            )
            features['capm_alpha'] = alpha
            features['capm_beta'] = beta
            features[date_col] = end_date
            hist_data.append(features)
        if not hist_data:
            return None
        return df.merge(pd.DataFrame(hist_data), on=date_col, how='left')

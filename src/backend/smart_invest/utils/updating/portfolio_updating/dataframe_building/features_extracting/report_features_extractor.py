import os
import json
import numpy as np
import pandas as pd


class ReportsFeaturesExtractor:

    def __init__(self, features):
        print(type(features))
        if isinstance(features, str) and os.path.splitext(features)[-1] == '.json':
            with open(features, 'r') as features_file:
                self.features = json.loads(features_file.read())
        elif isinstance(features, dict):
            self.features = features

    @staticmethod
    def select_or_set_nan(df, features):
        common_features = set(df.columns).intersection(features)
        missed_features = set(features).difference(set(df.columns))
        df = df.loc[:, list(common_features)]
        df[list(missed_features)] = np.nan
        return df

    def select_key_features(self, balance_sheet, income_stmt, cashflow, date_col='date'):
        balance_sheet = self.select_or_set_nan(balance_sheet, self.features['balance_key_features'])
        income_stmt = self.select_or_set_nan(income_stmt, self.features['income_stmt_key_features'])
        cashflow = self.select_or_set_nan(cashflow, self.features['cashflow_key_features'])
        df = balance_sheet.merge(income_stmt, how='inner', on=date_col).merge(cashflow, how='inner', on=date_col)
        df['enterprise_value'] = df['stockholders_equity'] + df['total_debt']
        return df

    def add_multiplicators(self, df):
        for muliplicator, (numerator, denominator) in self.features['multiplicators'].items():
            df[muliplicator] = df[numerator] / df[denominator]
        return df

    def add_diff_features(self, df, periods=None, date_col='date'):
        if periods is None:
            periods = [-1, -2]

        df = df.sort_values(by=date_col, ascending=False)
        data = []
        columns = []
        for feature in self.features['diff_features']:
            if feature == date_col:
                continue
            for period in periods:
                # Compute the absolute values of difference
                data.append(df[feature].diff(period).values)
                columns.append(f'{feature}_diff({period})')
                # Compute the relative values of difference
                data.append((data[-1] / df[feature]).values)
                columns.append(f'{feature}_diff({period})_rate')
        data.append(df.date.values)
        columns.append(date_col)
        data = pd.DataFrame(data=np.array(data).T, columns=columns)
        data[date_col] = pd.to_datetime(pd.to_datetime(data[date_col]).dt.date)
        return df.merge(data, on=date_col)





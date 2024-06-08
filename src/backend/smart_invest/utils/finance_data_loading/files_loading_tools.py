import os
import pandas as pd


def dir_check_and_create(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)


def create_or_append_csv(df, path_or_buf, cols_to_concat=None, date_col='date', index=False, duplicates_subset=None,  read_csv_params=None):
    if read_csv_params is None:
        read_csv_params = dict()
    if duplicates_subset is None:
        duplicates_subset = [date_col]
    if cols_to_concat is None:
        cols_to_concat = ['date', 'open', 'close', 'high', 'low', 'volume']

    if os.path.exists(path_or_buf):
        if os.path.isfile(path_or_buf) and os.path.splitext(path_or_buf)[-1] == '.csv':
            file_data = pd.read_csv(path_or_buf, parse_dates=[date_col], **read_csv_params)
            file_data = pd.concat([file_data.loc[:, cols_to_concat], df.loc[:, cols_to_concat]]).drop_duplicates(subset=duplicates_subset, ignore_index=True)\
                          .sort_values(by=[date_col])
            file_data.to_csv(path_or_buf=path_or_buf, index=index)
        else:
            raise ValueError('Invalid "path_or_buf" was passed')
    else:
        df = df.sort_values(by=date_col)
        df.to_csv(path_or_buf=path_or_buf, index=index)


def adjust_text_to_snack_case(text):
    return '_'.join(text.lower().split())
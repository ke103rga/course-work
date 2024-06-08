import json
import time
import pandas as pd
import yfinance as yf
from ..finance_data_loading import files_loading_tools as tools
from .. import settings


class YahooFinanceDownloader:
    invalid_tickers = dict()
    mismatched_tickers = []
    valid_tickers = dict()

    def __init__(self, top_tickers=None, data_directory=None):
        if top_tickers is None:
            with open(settings.TOP_TICKERS_PATH, 'r') as tickers_file:
                self.top_tickers = json.loads(tickers_file.read())
        else:
            self.top_tickers = top_tickers

        if data_directory is None:
            self.data_directory = settings.FINANCE_DATA_DIRECTORY
        else:
            self.data_directory = data_directory

    def download_sector_data(self, sector_name, sector_tickers, log_file=None):
        if log_file is None:
            log_file = f'{self.data_directory}\\download_log.txt'
        # Create directory for particular sector
        cur_sector_directory = f'{self.data_directory}\\{sector_name}'
        tools.dir_check_and_create(cur_sector_directory)
        # Init multiple tickers object
        sector_data = yf.Tickers(' '.join(sector_tickers))
        for cur_ticker in sector_tickers:
            # Set the name and create the directory for reports of particular sticker
            cur_ticker_directory = f'{cur_sector_directory}\\{cur_ticker}'
            tools.dir_check_and_create(cur_ticker_directory)
            # Download reports by api
            balance_sheet = sector_data.tickers[cur_ticker].quarterly_balance_sheet
            income_stmt = sector_data.tickers[cur_ticker].quarterly_income_stmt
            cashflow = sector_data.tickers[cur_ticker].quarterly_cashflow
            # Transparent reports in such way that strings of report become columns
            balance_sheet = balance_sheet.T
            income_stmt = income_stmt.T
            cashflow = cashflow.T
            # Add date as a feature
            balance_sheet['date'] = balance_sheet.index
            income_stmt['date'] = income_stmt.index
            cashflow['date'] = cashflow.index

            if any([balance_sheet.shape[0] == 0, income_stmt.shape[0] == 0, cashflow.shape[0] == 0]):
                with open(log_file, "a") as file:
                    if sector_name in self.invalid_tickers.keys():
                        self.invalid_tickers[sector_name].append(cur_ticker)
                    else:
                        self.invalid_tickers[sector_name] = [cur_ticker]
                    file.write(
                        f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())} '
                        f'ERROR: reports of ticker {cur_ticker.ljust(5)} do not contains any information\n')
                    continue

            # Check that all reports were published in the same date and save it
            if income_stmt.merge(balance_sheet, on='date', how='inner').merge(cashflow, on='date', how='inner') \
                    .shape[0] != max(income_stmt.shape[0], cashflow.shape[0], balance_sheet.shape[0]):
                with open(log_file, "a") as file:
                    self.mismatched_tickers.append((sector_name, cur_ticker))
                    file.write(
                        f'{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())} '
                        f'WARNING: reports of ticker {cur_ticker.ljust(5)} contains mismatched dates\n')

            # Restyle all features names to snack case
            balance_sheet.columns = [tools.adjust_text_to_snack_case(column) for column in balance_sheet.columns]
            income_stmt.columns = [tools.adjust_text_to_snack_case(column) for column in income_stmt.columns]
            cashflow.columns = [tools.adjust_text_to_snack_case(column) for column in cashflow.columns]

            # Saving data
            tools.create_or_append_csv(
                df=balance_sheet,
                path_or_buf=f'{cur_ticker_directory}\\quarterly_balance_sheet.csv',
                index=False
            )
            tools.create_or_append_csv(
                df=income_stmt,
                path_or_buf=f'{cur_ticker_directory}\\quarterly_income_statement.csv',
                index=False
            )
            tools.create_or_append_csv(
                df=cashflow,
                path_or_buf=f'{cur_ticker_directory}\\quarterly_cashflow.csv',
                index=False
            )

    def download_top_tickers_data(self, log_file=None):
        if log_file is None:
            log_file = f'{self.data_directory}\\download_log.txt'
        for sector_name, sector_tickers in self.top_tickers.items():
            self.download_sector_data(sector_name, sector_tickers, log_file)

        self.valid_tickers = {
            sector_name: list(set(self.top_tickers.get(sector_name, [])) \
                              .difference(set(self.invalid_tickers.get(sector_name, [])))) for
            sector_name in self.top_tickers.keys()
        }

        with open(f'{self.data_directory}\\valid_tickers.json', 'w') as valid_tickers_file:
            json.dump(
                {sector: list(tickers) for sector, tickers in self.valid_tickers.items()}, valid_tickers_file
            )

    def download_tickers_history(self, period='3y', interval='1d'):
        for cur_sector in self.top_tickers:
            for cur_ticker in self.top_tickers[cur_sector]:
                if cur_ticker == 'PEAK':
                    continue
                cur_ticker_obj = yf.Ticker(cur_ticker)
                history_data = cur_ticker_obj.history(period=period, interval=interval)
                history_data = history_data.reset_index()
                if history_data.shape[0] == 0:
                    continue
                history_data['date'] = pd.to_datetime(history_data['Date'].dt.date)
                history_data = history_data[['date', 'Open', 'Close', 'High', 'Low', 'Volume']]
                history_data.columns = [tools.adjust_text_to_snack_case(column) for column in history_data.columns]
                filename = f'{self.data_directory}\\{cur_sector}\\{cur_ticker}\\history.csv'
                tools.create_or_append_csv(history_data, filename)
                # history_data.to_csv(filename, index=False)

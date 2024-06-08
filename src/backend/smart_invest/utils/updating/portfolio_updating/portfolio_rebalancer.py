from pandas import DataFrame, concat, merge

from pandas import DataFrame, concat, merge


class PortfolioBalancer:
    """
    PortfolioBalancer class for balancing investment portfolios based on various criteria.

    :param ensemble: The ensemble model used for predicting portfolio-related parameters.
    :param common_data: Common data containing information about symbols, sectors, and market caps.

    Attributes:
    - _criterion_aliases (dict): A mapping of criterion aliases to their corresponding full names.

    Methods:
    - __init__(self, ensemble, common_data): Initialize the PortfolioBalancer with an ensemble model and common data.
    - predict(self, ensemble_predict_params): Make predictions using the ensemble model.
    - predict_fair_real_rates(self, ensemble_predict_params, orig_data): Predict fair real rates for given data.
    - compute_sector_cap(self, fair_real_rates, new_portfolio): Compute sector-wise market cap for new portfolio.
    - update_portfolio(self, fair_real_rates, new_portfolio, current_portfolio=None, top_n=5, criterion='fr'):
        Update the investment portfolio based on fair real rates and specified criteria.
    - calculate_portfolio_changes(self, new_portfolio, current_portfolio=None): Calculate changes in the portfolio.

    """

    _criterion_aliases = {
        'fr': 'fair_real_ratio',
        'mc': 'market_cap',
        'pi': 'potential_income'
    }

    def __init__(self, ensemble, common_data, tickers_from_sector=5, criterion='fr'):
        """
        Initialize the PortfolioBalancer.

        :param ensemble: The ensemble model used for predicting portfolio-related parameters.
        :param common_data: Data containing information about previous companies reports. Used to get
               market capitalisation of companies in previous report period and compute fair capitalisation
        """

        self.ensemble = ensemble
        self.common_data = common_data
        self.tickers_from_sector = tickers_from_sector
        self.criterion = criterion

    @staticmethod
    def select_closest_ndays(history, report_date, n=10, back=True):
        # print(report_date)
        deltas = (pd.to_datetime(report_date) - pd.to_datetime(history['date'].dt.date)).apply(lambda delta: delta.days)

        if back:
            closest_history = history.loc[deltas[deltas > 0].sort_values().head(n).index, ('open', 'close', 'date')]
        else:
            closest_history = history.loc[
                deltas[deltas < 0].sort_values(ascending=False).head(n).index, ('open', 'close', 'date')]
        closest_history['day_mean'] = closest_history.loc[:, ('open', 'close')].mean(axis=1)
        return closest_history.loc[:, ('date', 'day_mean')].sort_values(by=['date'])

    def get_actual_market_caps(self, report_date):

        last_share_numbers = self.common_data[self.common_data['date'] <= report_date].sort_values(
            by=['symbol', 'date'], ascending=False) \
                                 .groupby('symbol').head(1).loc[:, ('symbol', 'ordinary_shares_number')]

        actual_quotes = []
        for sector, symbol in self.common_data[['sector', 'symbol']].value_counts().reset_index()[
            ['sector', 'symbol']].values:
            # print(sector, symbol)
            history = pd.read_csv(f'{settings.FINANCE_DATA_DIRECTORY}\\{sector}\\{symbol}\\history.csv',
                                  parse_dates=['date'])
            last_qoutes = PortfolioBalancer.select_closest_ndays(history, report_date, 10, back=True)
            actual_qoute = last_qoutes['day_mean'].mean()
            actual_quotes.append([sector, symbol, actual_qoute])

        actual_market_caps = pd.merge(
            last_share_numbers,
            pd.DataFrame(columns=['sector', 'symbol', 'actual_quote'], data=actual_quotes),
            how='inner',
            on='symbol'
        )
        actual_market_caps['actual_market_cap'] = actual_market_caps['actual_quote'] * actual_market_caps[
            'ordinary_shares_number']
        return actual_market_caps.loc[:, ('sector', 'symbol', 'actual_market_cap')]

    def predict(self, ensemble_predict_params: dict) -> DataFrame:
        """
        Make predictions using the ensemble model.

        :param ensemble_predict_params: Parameters for predicting portfolio-related values.
        :return: Predicted values for the portfolio.
        """
        return self.ensemble.predict(**ensemble_predict_params)

    def predict_fair_real_rates(self, ensemble_predict_params: dict, orig_data: DataFrame, rebalance_date) -> DataFrame:
        """
        Predict the ratio of the fair value of the company to the market value by ensemble of models.

        :param ensemble_predict_params: Parameters for predicting fair_real ratio by ensemble.
        :param orig_data: Original (not preprocessed) data for which rates are predicted.
        :return: DataFrame with predicted fair real rates.
        """
        # Predict relative market cap difference for input data by ensemble
        predictions = self.predict(ensemble_predict_params)

        # To compute absolute fair capitalization necessary to know previous market cap for every ticker
        #  that information takes from common df
        prev_data = self.common_data[self.common_data['symbol'].isin(orig_data.symbol.unique())] \
                        .sort_values(by=['symbol', 'date'], ascending=False) \
                        .loc[:, ('sector', 'symbol', 'market_cap', 'date')]
        prev_data['prev_market_cap'] = prev_data.groupby('symbol')['market_cap'].shift(-1)

        # From original (not preprocessed) data extract only important features
        fair_real_rates = orig_data.loc[:, ('symbol', 'sector', 'date')]
        # Add information about predicted difference and previous values
        fair_real_rates['predictions'] = predictions
        fair_real_rates = fair_real_rates.merge(prev_data.loc[:, ('symbol', 'date', 'prev_market_cap')],
                                                on=['symbol', 'date'])
        # Taking only last (actual) reports data for every ticker
        fair_real_rates = fair_real_rates[fair_real_rates['date'] <= rebalance_date] \
            .sort_values(by=['symbol', 'date'], ascending=False) \
            .groupby('symbol').head(1)
        # Getting the actual market cap for particular date
        actual_market_caps = self.get_actual_market_caps(rebalance_date).loc[:, ('symbol', 'actual_market_cap')]
        fair_real_rates = fair_real_rates.merge(
            actual_market_caps,
            how='inner', on='symbol'
        )
        # Compute fair capitalisation via predicted difference and compare it with real cap
        fair_real_rates['fair_market_cup_via_diff'] = fair_real_rates['prev_market_cap'] + fair_real_rates[
            'prev_market_cap'] * fair_real_rates['predictions']
        fair_real_rates['fair_real_ratio'] = fair_real_rates['fair_market_cup_via_diff'] / fair_real_rates[
            'actual_market_cap']

        return fair_real_rates

    def compute_sector_cap(self, rebalance_date, new_portfolio: DataFrame) -> DataFrame:
        """
        Compute sector-wise total market capitalization of all companies for new portfolio.

        :param fair_real_rates: DataFrame with predicted the ratio of the fair value of the company to the market value.
        :param new_portfolio: DataFrame representing the new portfolio.
        :return: DataFrame with sector-wise total market capitalization of all companies.
        """
        # To define part of ticker in final portfolio it's necessary to know part of it sector in whole market cap.
        # To get that part we will take the latest info.
        # missed_tickers = self.common_data[~self.common_data['symbol'].isin(fair_real_rates.symbol.unique())] \
        #     .sort_values(by=['symbol', 'date'], ascending=False)
        # missed_tickers = missed_tickers.groupby('symbol').head(1).loc[:, ('sector', 'symbol', 'market_cap')]
        sector_cap = self.get_actual_market_caps(rebalance_date)
        sector_cap = sector_cap.groupby('sector').agg(**{'total_cap': ('actual_market_cap', 'sum')}).reset_index()
        sector_cap = sector_cap[sector_cap['sector'].isin(new_portfolio.sector.unique())]
        sector_cap['part_of_market'] = sector_cap['total_cap'].divide(sector_cap['total_cap'].sum())
        return sector_cap

    def update_portfolio(self, fair_real_rates: DataFrame, current_portfolio: DataFrame = None) -> DataFrame:
        """
        Update the investment portfolio based on fair real rates and specified criteria.
        First of all the ratio of the fair value of the company to the market value predicts, to detect underrated
        companies, after it drops all overrated companies (fair_real rate <= 1) and among the remaining companies
        selects top_n by set criterion.

        :param fair_real_rates: DataFrame with predicted the ratio of the fair value of the company to the market value.
        :param current_portfolio: DataFrame representing the current portfolio (optional).
        :param top_n: Number of top tickers to consider from every sector in the updated portfolio.
        :param criterion: Criteria for selecting top tickers.Criterion values:
               'fr': fair_real rate (The most underrated companies will be selected to the new portfolio)
               'mc': market capitalization of company (The most expensive companies will be selected to the new portfolio)
               'pi': potential income which was computed like ((fair_real rate - 1) * market capitalization)
                     (The most potentially profitable companies will be selected to the new portfolio)
        :return: Updated DataFrame representing the investment portfolio.
        """
        if current_portfolio is None:
            current_portfolio = DataFrame(columns=['sector', 'symbol', 'fair_real_ratio', 'actual_market_cap'])

        # To update a portfolio necessary update fair_real_rates for input data
        # At the same time we should save last rates for tickers which weren't updated
        new_portfolio = concat([
            fair_real_rates.loc[:, ('sector', 'symbol', 'fair_real_ratio', 'actual_market_cap')],
            current_portfolio[~current_portfolio['symbol'].isin(fair_real_rates.symbol.unique())] \
                .loc[:, ('sector', 'symbol', 'fair_real_ratio', 'actual_market_cap')]
        ])

        # Take top tickers by 'fair_real_ratio' and drop all which value less than 1
        new_portfolio = new_portfolio[new_portfolio['fair_real_ratio'] > 1]

        # To define part of ticker in final portfolio it's necessary to know part of it sector in whole market cap.
        # To get that part we will take the latest info.
        sector_cap = self.compute_sector_cap(fair_real_rates['date'].max(), new_portfolio)

        feature_criterion = self._criterion_aliases.get(self.criterion, 'fair_real_ratio')
        # print(feature_criterion)
        if feature_criterion == 'pothential_income':
            new_portfolio['pothential_income'] = new_portfolio['actual_market_cap'] * (
                new_portfolio['fair_real_ratio'].sub(1))

        new_portfolio = new_portfolio.sort_values(by=['sector', 'fair_real_ratio'], ascending=False).groupby(
            'sector').head(self.tickers_from_sector)

        # Compute total rates for every sector
        total = new_portfolio.groupby('sector').agg(**{'total': (feature_criterion, 'sum')}).reset_index()

        new_portfolio = new_portfolio.sort_values(by=['sector', feature_criterion], ascending=False) \
            .groupby('sector').head(self.tickers_from_sector)

        new_portfolio = new_portfolio.merge(sector_cap.loc[:, ('sector', 'part_of_market')], on='sector') \
            .merge(total, on='sector')
        # Compute portfolio part by formula
        new_portfolio['portfolio_part'] = new_portfolio[feature_criterion] / new_portfolio['total'] * new_portfolio[
            'part_of_market']

        return new_portfolio

    def calculate_portfolio_changes(self, new_portfolio: DataFrame, current_portfolio: DataFrame) -> DataFrame:
        """
        Calculate changes in the portfolio.

        :param new_portfolio: DataFrame representing the new portfolio. It should contain columns: 'sector',
               'symbol', 'portfolio_part'
        :param current_portfolio: DataFrame representing the current portfolio (optional). It should contain the same
               columns as new_portfolio
        :return: DataFrame with changes in the portfolio.
        """
        if current_portfolio is None:
            portfolio_changes = new_portfolio.loc[:, ('sector', 'symbol', 'portfolio_part')].rename(
                columns={'portfolio_part': 'new_portfolio_part'})
            portfolio_changes['change'] = portfolio_changes['new_portfolio_part']
            return portfolio_changes

        portfolio_changes = merge(
            current_portfolio.loc[:, ('sector', 'symbol', 'portfolio_part')].rename(
                columns={'portfolio_part': 'old_portfolio_part'}),
            new_portfolio.loc[:, ('sector', 'symbol', 'portfolio_part')].rename(
                columns={'portfolio_part': 'new_portfolio_part'}),
            on=['symbol', 'sector'], how='outer'
        ).fillna(0)
        portfolio_changes['change'] = portfolio_changes['new_portfolio_part'] - portfolio_changes['old_portfolio_part']
        return portfolio_changes

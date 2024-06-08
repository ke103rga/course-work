
from django.db import models
import sys
from utils import loading_tools
from utils import settings as utils_setings
# from .utils.updating.portfolio_updating.data_preprocessors import ToNumDataPreprocessor, ToNumAndCatDataPreprocessor
# from .utils.updating.portfolio_updating.fair_rates_predicting.blending_ensemble_predictor import BlendingEnsemble
# from .utils.updating.portfolio_updating.dataframe_building.target.smoother import MeanSmoother


class News(models.Model):
    original_id = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    article_url = models.URLField()
    image_url = models.URLField()
    description = models.CharField(max_length=500)
    published_utc = models.DateTimeField()
    tickers = models.TextField()
    publisher_name = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Strategy(models.Model):
    name = models.CharField(max_length=50)
    features_file = models.FilePathField()
    target_smoother_file = models.FilePathField()
    to_num_prep_file = models.FilePathField()
    to_num_and_cat_prep_file = models.FilePathField()
    predictor_file = models.FilePathField()
    criterion = models.CharField(max_length=30)
    target_n_days = models.IntegerField()
    tickers_from_sector = models.IntegerField()

    def __str__(self):
        return (f'Strategy: criterion: {self.criterion}; '
                f'Amount of days: {self.target_n_days}; '
                f'Tickers from sector: {self.tickers_from_sector}')

    @property
    def features(self):
        return loading_tools.load_features(self.features_file)

    @property
    def target_smoother(self):
        return loading_tools.load_model(self.target_smoother_file)

    @property
    def to_num_preprocessor(self):
        return loading_tools.load_model(self.to_num_prep_file)

    @property
    def to_num_and_cat_preprocessor(self):
        return loading_tools.load_model(self.to_num_and_cat_prep_file)

    @property
    def predictor(self):
        return loading_tools.load_model(self.predictor_file)


class PortfolioComposition(models.Model):
    strategy_id = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    stock_name = models.CharField(max_length=50)
    part = models.FloatField()
    #TODO
    # Change the field type into date field and reload the data
    creation_date = models.DateTimeField()
    sector = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.sector}; {self.stock_name}; {self.part}'


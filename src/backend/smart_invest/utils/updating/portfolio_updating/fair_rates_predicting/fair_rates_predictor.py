import abc
from pandas import DataFrame


class FairRatesPredictor(abc.ABC):
    @abc.abstractmethod
    def fit(self, num_dataset: DataFrame, num_cat_dataset: DataFrame):
        pass

    @abc.abstractmethod
    def predict(self, num_X: DataFrame, num_cat_X: DataFrame):
        pass

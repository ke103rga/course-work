import abc
from pandas import DataFrame, concat
from numpy import concatenate, array, number
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer


class DataPreprocessor(abc.ABC):
    @abc.abstractmethod
    def fit(self, data: DataFrame, cols_to_ignore: list[str]):
        pass

    @abc.abstractmethod
    def transform(self, data: DataFrame, cols_to_ignore: list[str]):
        pass

    @abc.abstractmethod
    def fit_transform(self, data: DataFrame, cols_to_ignore: list[str]):
        pass


class ToNumDataPreprocessor(DataPreprocessor):
    def __init__(self):
        self.num_transformer = Pipeline(steps=[("scaler", StandardScaler())])
        self.cat_transformer = Pipeline(steps=[("OHE", OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
        self.data_cat_features = None
        self.data_preprocessor = None

    def fit(self, data, cols_to_ignore=None):
        if cols_to_ignore is None:
            cols_to_ignore = []
        if not isinstance(data, DataFrame):
            raise ValueError('Passed data should be pandas DataFrame')
        num_features = data.drop(columns=cols_to_ignore).select_dtypes(include=number).columns.tolist()
        cat_features = data.drop(columns=cols_to_ignore).select_dtypes(include=["object"]).columns.tolist()
        self.data_cat_features = cat_features
        self.data_preprocessor = ColumnTransformer(transformers=[('num', self.num_transformer, num_features),
                                                                 ("cat", self.cat_transformer, cat_features)],
                                                   remainder='passthrough')
        self.data_preprocessor.fit(data.drop(columns=cols_to_ignore))

    def transform(self, data, cols_to_ignore=None):
        if cols_to_ignore is None:
            cols_to_ignore = []
        preprocessed_data = self.data_preprocessor.transform(data.drop(columns=cols_to_ignore))
        ignore_data = data[cols_to_ignore]
        new_num_names = self.data_preprocessor.transformers_[0][2].copy()
        new_cat_names = self.data_preprocessor.transformers_[1][1].named_steps['OHE'].get_feature_names_out(self.data_cat_features).copy()
        new_names = concatenate((array(new_num_names, dtype="object"), new_cat_names))
        preprocessed_data = DataFrame(data=preprocessed_data, columns=new_names, index=data.index)
        preprocessed_data = concat([preprocessed_data, ignore_data], axis=1)
        return preprocessed_data

    def fit_transform(self, data, cols_to_ignore=None):
        if cols_to_ignore is None:
            cols_to_ignore = []
        self.fit(data, cols_to_ignore=cols_to_ignore)
        preprocessed_data = self.transform(data, cols_to_ignore=cols_to_ignore)
        return preprocessed_data


class ToNumAndCatDataPreprocessor(DataPreprocessor):
    def __init__(self):
        self.num_transformer = Pipeline(steps=[("scaler", StandardScaler())])
        self.data_preprocessor = None
        self.num_preprocessor = None

    def fit(self, data, cols_to_ignore=[]):
        if not isinstance(data, DataFrame):
            raise ValueError('Passed data should be pandas DataFrame')
        num_features = data.drop(columns=cols_to_ignore).select_dtypes(include=number).columns.tolist()
        cat_features = data.select_dtypes(include=["object"]).columns.tolist()
        self.num_preprocessor = ColumnTransformer(transformers=[('num', self.num_transformer, num_features)],
                                                  remainder='passthrough')
        self.num_preprocessor.fit(data.drop(columns=cat_features))
        self.num_preprocessor.fit(data.drop(columns=cols_to_ignore))

    def transform(self, data, cols_to_ignore=[]):
        if not isinstance(data, DataFrame):
            raise ValueError('Passed data should be pandas DataFrame')
        cat_features = data.drop(columns=cols_to_ignore).select_dtypes(include=["object"]).columns.tolist()
        ignore_data = data[cols_to_ignore]
        preprocessed_data = self.num_preprocessor.transform(data.drop(columns=cols_to_ignore))
        new_names = self.num_preprocessor.transformers_[0][2].copy()
        preprocessed_data = DataFrame(data=preprocessed_data, columns=new_names + cat_features, index=data.index)
        # print(preprocessed_data.dtypes[0])
        preprocessed_data[new_names] = preprocessed_data[new_names].astype(float)
        preprocessed_data = concat([preprocessed_data, ignore_data], axis=1)
        return preprocessed_data

    def fit_transform(self, data, cols_to_ignore=[]):
        if not isinstance(data, DataFrame):
            raise ValueError('Passed data should be pandas DataFrame')
        self.fit(data, cols_to_ignore)
        preprocessed_data = self.transform(data, cols_to_ignore)
        return preprocessed_data




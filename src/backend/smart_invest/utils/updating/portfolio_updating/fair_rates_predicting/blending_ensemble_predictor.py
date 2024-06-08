from numpy import hstack
from sklearn.model_selection import GridSearchCV
from .fair_rates_predictor import FairRatesPredictor


class BlendingEnsemble(FairRatesPredictor):
    def __init__(self, estimators, meta_model):
        if not isinstance(estimators, list) and all((isinstance(estimator, tuple) for estimator in estimators)):
            raise ValueError(
                "'estimators' param should be in format: [(estimator, type_of_dataset), (estimator, type_of_dataset)]\n" +
                "Where possible types of datasets are: 'cat' and 'num'.")
        self.estimators = estimators
        self.meta_model = meta_model

    def check_datasets(self, num_dataset, cat_dataset):
        if not (isinstance(num_dataset, tuple) and len(num_dataset) == 4):
            raise ValueError("'num_dataset' param should be in format: (X_test, y_test, X_train, y_train)")
        if not cat_dataset is None and not (isinstance(cat_dataset, tuple) and len(cat_dataset) == 4):
            raise ValueError("'cat_dataset' param should be in format: (X_test, y_test, X_train, y_train)")

    def fit_generator(self, num_dataset, cat_dataset):
        for est, dataset_key in self.estimators:
            if dataset_key == 'num':
                X_train, y_train, X_test, y_test = num_dataset
            elif dataset_key == 'cat':
                X_train, y_train, X_test, y_test = cat_dataset
            else:
                raise ValueError(
                    f"Unknown type of dataset for estimator: {est.__class__.__name__}. "
                    f"Possible types of datasets are: 'cat' and 'num'.")
            yield est, (X_train, y_train, X_test, y_test)

    def predict_generator(self, num_X, cat_X):
        for est, dataset_key in self.estimators:
            if dataset_key == 'num':
                yield est, num_X
            elif dataset_key == 'cat':
                yield est, cat_X
            else:
                raise ValueError(
                    f"Unknown type of dataset for estimator: {est.__class__.__name__}. "
                    f"Possible types of datasets are: 'cat' and 'num'.")

    def fit(self, num_dataset, cat_dataset=None, X=None, y=None):
        self.check_datasets(num_dataset, cat_dataset)

        meta_X = []
        for est, dataset in self.fit_generator(num_dataset, cat_dataset):
            X_train, y_train, X_test, y_test = dataset
            est.fit(X_train, y_train)
            predictions = est.predict(X_test)
            meta_X.append(predictions.reshape(-1, 1))
        meta_X = hstack(meta_X)
        self.meta_model.fit(meta_X, y_test)
        print(self.meta_model.coef_)

    def predict(self, num_X, cat_X=None):
        meta_X = []
        for est, X in self.predict_generator(num_X, cat_X):
            predictions = est.predict(X)
            meta_X.append(predictions.reshape(-1, 1))
        meta_X = hstack(meta_X)
        return self.meta_model.predict(meta_X)

    def meta_model_grid_search(self, params_grid, scoring, num_dataset, cat_dataset=None, cv=5, update_meta_model=True):
        self.check_datasets(num_dataset, cat_dataset)
        meta_X = []
        for est, dataset in self.fit_generator(num_dataset, cat_dataset):
            X_train, y_train, X_test, y_test = dataset
            est.fit(X_train, y_train)
            predictions = est.predict(X_test)
            meta_X.append(predictions.reshape(-1, 1))
        meta_X = hstack(meta_X)
        grid = GridSearchCV(estimator=self.meta_model, param_grid=params_grid, scoring=scoring,
                            n_jobs=3, cv=cv, verbose=0)
        grid.fit(meta_X, y_test)
        if update_meta_model:
            self.meta_model = grid.best_estimator_
        return grid.best_estimator_

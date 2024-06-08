import json
import joblib
from .. import settings


def save_model_params(fitted_estimator, filename=None, params_dir=None):
    if params_dir is None:
        params_dir = settings.ML_MODELS_PARAMS_DIRECTORY
    if filename is None:
        filepath = f'{params_dir}\\{fitted_estimator.__class__.__name__}_params.json'
    else:
        filepath = f'{params_dir}\\{filename}.json'
    with open(filepath, 'w') as params_file:
        json.dump(fitted_estimator.get_params(), params_file)


def read_model_params(filename, params_dir=None):
    if params_dir is None:
        params_dir = settings.ML_MODELS_PARAMS_DIRECTORY
    with open(f'{params_dir}\\{filename}.json', 'r') as params_file:
        est_params = json.loads(params_file.read())
    return est_params


def save_model(model, filename=None, models_dir=None):
    if models_dir is None:
        models_dir = settings.ML_MODELS_PARAMS_DIRECTORY
    if filename is None:
        filename = f'{models_dir}\\{model.__class__.__name__}.pkl'
    joblib.dump(model, filename)


def load_model(filename):
    if filename.contains('\\') or filename.contains('/') :
        model = joblib.load(filename)
    else:
        models_dir = settings.ML_MODELS_PARAMS_DIRECTORY
        model = joblib.load(f'{models_dir}\\{filename}')
    return model

import os

cwd = os.getcwd() + '\\utils'

# elf.FEATURES_DATA_DIRECTORY = f"{cwd}\\data\\features_data"
# self.FINANCE_DATA_DIRECTORY = f"{cwd}\\data\\finance_data"
# self.MODELS_DIRECTORY = f"{cwd}\\ml_models"
# self.QUOTES_DIRECTORY = f"{cwd}\\data\\quotes_data"
# self.STRATEGIES_DIRECTORY = f"{cwd}\\data\\strategies_data"
#
# self.TOP_TICKERS_PATH = f"{self.FINANCE_DATA_DIRECTORY}\\top_tickers.json"
# self.VALID_TICKERS_PATH = f"{self.FINANCE_DATA_DIRECTORY}\\valid_tickers.json"
# self.MAIN_TICKERS_PATH = f"{self.FINANCE_DATA_DIRECTORY}\\main_tickers.json"
#
# self.BASE_FEATURES_PATH = f'{self.FEATURES_DATA_DIRECTORY}\\base_features.json'
# self.FEATURES_PATH = f'{self.FEATURES_DATA_DIRECTORY}\\features.json'
# self.FINAL_FEATURES_PATH = f'{self.FEATURES_DATA_DIRECTORY}\\final_features.json'
#
# self.ML_FITTED_MODELS_DIRECTORY = f"{self.MODELS_DIRECTORY}\\fitted_ml_models"
# self.ML_MODELS_PARAMS_DIRECTORY = f"{self.MODELS_DIRECTORY}\\ml_models_params"
# self.FITTED_PREPROCESSORS_DIRECTORY = f"{self.MODELS_DIRECTORY}\\preprocessors"

FEATURES_DATA_DIRECTORY = f"{cwd}\\data\\features_data"
FINANCE_DATA_DIRECTORY = f"{cwd}\\data\\finance_data"
MODELS_DIRECTORY = f"{cwd}\\data\\ml_models"
QUOTES_DIRECTORY = f"{cwd}\\data\\quotes_data"
STRATEGIES_DIRECTORY = f"{cwd}\\data\\strategies_data"
MAIN_TICKERS_PATH = f"{FINANCE_DATA_DIRECTORY}\\main_tickers.json"

MARKET_DATA_PATH = f"{FINANCE_DATA_DIRECTORY}\\market_data.csv"

TOP_TICKERS_PATH = f"{FINANCE_DATA_DIRECTORY}\\top_tickers.json"
VALID_TICKERS_PATH = f"{FINANCE_DATA_DIRECTORY}\\valid_tickers.json"

BASE_FEATURES_PATH = f'{FEATURES_DATA_DIRECTORY}\\base_features.json'
FEATURES_PATH = f'{FEATURES_DATA_DIRECTORY}\\features.json'
FINAL_FEATURES_PATH = f'{FEATURES_DATA_DIRECTORY}\\final_features.json'

ML_FITTED_MODELS_DIRECTORY = f"{MODELS_DIRECTORY}\\fitted_ml_models"
ML_MODELS_PARAMS_DIRECTORY = f"{MODELS_DIRECTORY}\\ml_models_params"
FITTED_PREPROCESSORS_DIRECTORY = f"{MODELS_DIRECTORY}\\preprocessors"
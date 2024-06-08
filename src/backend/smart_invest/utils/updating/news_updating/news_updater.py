from datetime import datetime, timedelta
import json
from pathlib import Path
from datetime import date
from main_app.models import News
from .news_loader import NewsLoader
from .news_preprocessor import NewsPreprocessor


class NewsUpdater:
    def __init__(self, news_loader: NewsLoader, news_preprocessor: NewsPreprocessor):
        self.news_loader = news_loader
        self.news_preprocessor = news_preprocessor
        self.setting_file = Path(__file__).resolve().parent.parent / "updating_settings.json"

    def get_updating_params(self):
        with open(self.setting_file, 'r') as settings_data:
            settings = json.load(settings_data)

        params = {
            'limit': settings['news_updating']['updating_limit'],
            'published_utc.gt': settings['news_updating']['last_update_date']
        }
        return params
    # from utils.updating.news_updating.news_updater import NewsUpdater as nu
    def upgrade_updating_params(self):
        with open(self.setting_file, 'r') as setting_file:
            settings = json.load(setting_file)

        settings['news_updating']['last_update_date'] = str(date.today())

        with open(self.setting_file, 'w') as setting_file:
            json.dump(settings, setting_file)

    def save_to_db(self, news):
        for one_news in news:
            one_news['original_id'] = one_news.pop('id')
            one_news['tickers'] = ', '.join(one_news['tickers'])
            News.objects.create(**one_news)

    def drop_old_news(self, ndays=3):
        print('Deleting old news')
        # delete all news from db which were loaded earlier than ndays
        last_ndays = datetime.now() - timedelta(days=ndays)
        print(last_ndays)
        old_news = News.objects.filter(published_utc__lte=last_ndays)
        print(old_news)
        old_news.delete()
        print('Deleting should be done')

    def update(self):
        query_params = self.get_updating_params()
        loaded_news = self.news_loader.load_news(query_params)
        if loaded_news:
            preprocessed_news = self.news_preprocessor.preprocess_news(loaded_news)
            self.save_to_db(preprocessed_news)
            self.drop_old_news()
            self.upgrade_updating_params()
            return preprocessed_news

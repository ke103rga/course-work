import abc
from deep_translator import GoogleTranslator


class NewsPreprocessor(abc.ABC):
    @abc.abstractmethod
    def preprocess_news(self, news: list[dict]):
        pass


class DefaultNewsPreprocessor(NewsPreprocessor):
    _fields_to_select = [
        'id',
        'title',
        'author',
        'published_utc',
        'article_url',
        'tickers',
        'image_url',
        'description'
    ]

    _fields_to_translate = [
        'title',
        'description'
    ]

    def __init__(self):
        self.translator = GoogleTranslator(source='auto', target='ru')

    def translate(self, one_news: dict):

        for field in self._fields_to_translate:
            one_news[field] = self.translator.translate(one_news[field])

        return one_news

    def select_news_fields(self, one_news: dict):
        preprocessed_one_news = {
            field: one_news[field] for field in self._fields_to_select
        }
        preprocessed_one_news['publisher_name'] = one_news['publisher']['name']

        return preprocessed_one_news

    def preprocess_news(self, news: list[dict]):
        preprocessed_news = []
        for one_news in news:
            preprocessed_one_news = self.select_news_fields(one_news)
            preprocessed_one_news = self.translate(preprocessed_one_news)
            preprocessed_news.append(preprocessed_one_news)

        return preprocessed_news

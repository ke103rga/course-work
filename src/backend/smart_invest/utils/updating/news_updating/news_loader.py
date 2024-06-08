import requests
import abc


class NewsLoader(abc.ABC):
    @abc.abstractmethod
    def load_news(self, query_params: dict[str, str]):
        pass


class PolygonNewsLoader(NewsLoader):
    _query_url = 'https://api.polygon.io/v2/reference/news?'

    def __init__(self, api_key):
        self.api_key = api_key

    def parse_query_params(self, query_params: dict[str, str]):
        query = self._query_url
        for key, param in query_params.items():
            query += f'&{key}={param}'
        query += f'&apiKey={self.api_key}'
        return query

    def load_news(self, query_params: dict[str, str]):
        query = self.parse_query_params(query_params)
        print(query)
        response = requests.get(query)

        if response:
            response = response.json()
            if response['status'] == 'OK':
                return response['results']

        return None


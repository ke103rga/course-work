from django.http import HttpResponse, JsonResponse

from utils.api_loading import ApiLoader


api_loader = ApiLoader()


def combine_jsons(*json_objects):
    return [json_object.items() for json_object in json_objects]


def index(request):
    return HttpResponse('<h2>Visiting the main page</h2>')


def get_news(request, limit):
    top_news = api_loader.load_news(limit=limit)
    return JsonResponse(top_news)


def get_main_tickers_data(request):
    main_tickers_data = api_loader.load_main_tickers_data()
    return JsonResponse(main_tickers_data)


def get_incorrect_rated_shares(request):
    incorrect_rated_shares = api_loader.load_incorrect_rated_shares()
    return JsonResponse(incorrect_rated_shares)


def get_ticker_history(request, ticker):
    ticker_history = api_loader.load_ticker_history(ticker)
    return JsonResponse(ticker_history)


def get_strategies_info(request, strategy_id=1):
    strategies_info = api_loader.load_strategies_info(strategy_id)
    return JsonResponse(strategies_info)


def get_actual_portfolio(request, strategy_id=1):
    actual_portfolio = api_loader.load_actual_portfolio(strategy_id)
    return JsonResponse(actual_portfolio)




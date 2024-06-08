
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index),
    path("news/<int:limit>/", views.get_news),
    path("main_tickers_data/", views.get_main_tickers_data),
    path("incorrect_rated_shares", views.get_incorrect_rated_shares),
    path("ticker_history/<slug:ticker>/", views.get_ticker_history),
    # re_path(r'ticker_history(?P<ticker>[\w+])/', views.get_ticker_history),
    # path("ticker_history?ticker=<slug:ticker>/", views.get_ticker_history),
    path("strategies_info/", views.get_strategies_info),
    path("actual_portfolio/", views.get_actual_portfolio),
]

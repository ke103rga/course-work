from apscheduler.schedulers.background import BackgroundScheduler
from decouple import config
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent))
from utils.updating import news_updating, stat_updating, portfolio_updating


def init_updaters():
    news_loader = news_updating.news_loader.PolygonNewsLoader(config("POLYGON_API_KEY"))
    news_preprocessor = news_updating.news_preprocessor.DefaultNewsPreprocessor()
    news_updater = news_updating.news_updater.NewsUpdater(news_loader, news_preprocessor)

    stat_updater = stat_updating.StatUpdater()
    portfolio_updater = portfolio_updating.PortfolioUpdater()

    return news_updater, stat_updater, portfolio_updater


def start():
    news_updater, stat_updater, portfolio_updater = init_updaters()

    scheduler = BackgroundScheduler()

    # scheduler.add_job(news_updater.update, 'cron', day='*', hour=20)
    # scheduler.add_job(stat_updater.update, 'cron', day='*', hour=20)
    # scheduler.add_job(stat_updater.update, 'cron', month='*', day='1st mon', hour=20)

    scheduler.start()




from django.apps import AppConfig
import sys
from pathlib import Path


# sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
# print(sys.path)


class MainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_app'

    def ready(self):
        print(sys.path)
        from utils.scheduling import scheduler
        scheduler.start()

        # start()

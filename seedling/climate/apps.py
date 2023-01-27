from django.apps import AppConfig


from .pump_controller import config_board


class ClimateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'seedling.climate'

    def ready(self) -> None:
        config_board()

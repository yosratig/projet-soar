from django.apps import AppConfig

class SoarConfig(AppConfig):
    name = 'soar'

    def ready(self):
        import soar.signals

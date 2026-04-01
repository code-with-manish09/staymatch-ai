from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts' # Aapke app ka naam

    def ready(self):
        import accounts.signals # Signals ko register kar raha hai
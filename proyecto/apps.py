from django.apps import AppConfig


class ProyectoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proyecto'

    def ready(self):
        import proyecto.signals

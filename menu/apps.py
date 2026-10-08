from django.apps import AppConfig


class MenuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'menu'
    verbose_name = 'Carta'

    def ready(self):
        from django.contrib import admin

        admin.site.site_header = "Vila's — Administración"
        admin.site.site_title = "Vila's"
        admin.site.index_title = 'Gestión de la carta'

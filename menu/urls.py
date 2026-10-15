from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.MenuView.as_view(), name='index'),
    path(_('sobre-nosotros/'), views.AboutView.as_view(), name='about'),
]

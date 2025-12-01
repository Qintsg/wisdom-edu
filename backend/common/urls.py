"""Common app URL bindings.

This module keeps lightweight shared endpoints, such as navigation metadata,
grouped under the `common` app namespace.
"""

from django.urls import path

from . import views

urlpatterns = [
    # Frontend shells request the menu tree from a stable, app-local endpoint.
    path('menu', views.get_menu, name='get_menu'),
]

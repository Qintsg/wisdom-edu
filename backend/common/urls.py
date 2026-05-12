"""Common app URL bindings.

This module keeps lightweight shared endpoints, such as navigation metadata,
grouped under the `common` app namespace.
"""

from django.urls import path

from common.api.views import get_menu

urlpatterns = [
    # Frontend shells request the menu tree from a stable, app-local endpoint.
    path('menu', get_menu, name='get_menu'),
]

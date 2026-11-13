# File: dadjokes/apps.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 11/13/2026
# Description: Configure the Dad Jokes application.

from django.apps import AppConfig


class DadjokesConfig(AppConfig):
    """Configure the app name and default primary key."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dadjokes'

# File: mini_insta/apps.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Configure the Mini Insta application.

from django.apps import AppConfig


class MiniInstaConfig(AppConfig):
    """Configure the Mini Insta application for Django."""

    # Match the primary key type used by the existing migrations.
    default_auto_field = 'django.db.models.BigAutoField'

    # Identify the application package.
    name = 'mini_insta'

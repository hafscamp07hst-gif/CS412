# File: voter_analytics/apps.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 10/30/2026
# Description: Configure the Voter Analytics application.

from django.apps import AppConfig


class VoterAnalyticsConfig(AppConfig):
    """Configure the Voter Analytics application for Django."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'voter_analytics'

# File: voter_analytics/urls.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 10/30/2026
# Description: Connect the voter list, detail, and graph pages.

from django.urls import path
from . import views

app_name = 'voter_analytics'

urlpatterns = [
    path('', views.VoterListView.as_view(), name='voters'),
    path('graphs', views.VoterGraphsView.as_view(), name='graphs'),
    path('voter/<int:pk>', views.VoterDetailView.as_view(), name='voter'),
]

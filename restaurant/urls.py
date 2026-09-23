# File: restaurant/urls.py
# Name: Sung Tae Hwang
# BU Email: sthwang@bu.edu
# Description: Define the URL routes for the restaurant's main page,
# order form, and order confirmation.
from django.urls import path
from . import views

app_name = "restaurant"

urlpatterns = [
    path(r'', views.main, name='main'),
    path(r'main', views.main, name='main'),
    path(r'order', views.order, name = 'order'),
    path(r'confirmation', views.confirmation, name ='confirmation'),
]
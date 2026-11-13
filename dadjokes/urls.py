# File: dadjokes/urls.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 11/13/2026
# Description: Connect joke and picture pages and REST API endpoints.

from django.urls import path
from . import views

app_name = 'dadjokes'

urlpatterns = [
    path('', views.random_joke, name='home'),
    path('random', views.random_joke, name='random'),
    path('jokes', views.JokeListView.as_view(), name='jokes'),
    path('joke/<int:pk>', views.JokeDetailView.as_view(), name='joke'),
    path('pictures', views.PictureListView.as_view(), name='pictures'),
    path('picture/<int:pk>', views.PictureDetailView.as_view(), name='picture'),

    # API views.
    path('api/', views.RandomJokeAPIView.as_view(), name='api'),
    path('api/random', views.RandomJokeAPIView.as_view(), name='random_api'),
    path('api/jokes', views.JokeListAPIView.as_view(), name='jokes_api'),
    path('api/joke/<int:pk>', views.JokeDetailAPIView.as_view(), name='joke_api'),
    path('api/pictures', views.PictureListAPIView.as_view(), name='pictures_api'),
    path('api/picture/<int:pk>', views.PictureDetailAPIView.as_view(), name='picture_api'),
    path('api/random_picture', views.RandomPictureAPIView.as_view(), name='random_picture_api'),
]

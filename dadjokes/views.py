# File: dadjokes/views.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 11/13/2026
# Description: Display joke and picture pages and provide their REST API views.

import random

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from rest_framework import generics
from .models import Joke, Picture
from .serializers import JokeSerializer, PictureSerializer


def random_joke(request):
    """Display one joke and one picture selected independently at random."""
    jokes = Joke.objects.all()
    pictures = Picture.objects.all()

    context = {
        'joke': random.choice(jokes) if jokes else None,
        'picture': random.choice(pictures) if pictures else None,
    }
    return render(request, 'dadjokes/random.html', context)


class JokeListView(ListView):
    """Display all jokes without pictures."""

    model = Joke
    template_name = 'dadjokes/jokes.html'
    context_object_name = 'jokes'


class JokeDetailView(DetailView):
    """Display one joke selected by its primary key."""

    model = Joke
    template_name = 'dadjokes/joke.html'
    context_object_name = 'joke'


class PictureListView(ListView):
    """Display all pictures without jokes."""

    model = Picture
    template_name = 'dadjokes/pictures.html'
    context_object_name = 'pictures'


class PictureDetailView(DetailView):
    """Display one picture selected by its primary key."""

    model = Picture
    template_name = 'dadjokes/picture.html'
    context_object_name = 'picture'


# REST API views.
class JokeListAPIView(generics.ListCreateAPIView):
    """Return all jokes or create one new joke from a POST request."""

    queryset = Joke.objects.all()
    serializer_class = JokeSerializer


class JokeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete one joke selected by its primary key."""

    queryset = Joke.objects.all()
    serializer_class = JokeSerializer


class RandomJokeAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Return one joke selected at random."""

    queryset = Joke.objects.all()
    serializer_class = JokeSerializer

    def get_object(self):
        """Return a random joke."""
        jokes = Joke.objects.all()
        return random.choice(jokes)


class PictureListAPIView(generics.ListCreateAPIView):
    """Return all pictures or create one picture from a POST request."""

    queryset = Picture.objects.all()
    serializer_class = PictureSerializer


class PictureDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete one picture selected by its primary key."""

    queryset = Picture.objects.all()
    serializer_class = PictureSerializer


class RandomPictureAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Return one picture selected at random."""

    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

    def get_object(self):
        """Return a random picture."""
        pictures = Picture.objects.all()
        return random.choice(pictures)

# File: dadjokes/models.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 11/13/2026
# Description: Store jokes and pictures as independent records.

from django.db import models


class Joke(models.Model):
    """Store one joke, its contributor, and its creation time."""

    text = models.TextField()
    name = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the joke text and contributor."""
        return f'{self.text} by {self.name}'


class Picture(models.Model):
    """Store one picture URL without a relationship to a joke."""

    image_url = models.URLField()
    name = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the picture URL and contributor."""
        return f'{self.image_url} by {self.name}'

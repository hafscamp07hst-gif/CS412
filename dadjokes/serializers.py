# File: dadjokes/serializers.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 11/13/2026
# Description: Convert joke and picture records to and from JSON data.

from rest_framework import serializers
from .models import Joke, Picture


class JokeSerializer(serializers.ModelSerializer):
    """Serialize joke records and validate new joke submissions."""

    class Meta:
        model = Joke
        fields = ['id', 'text', 'name', 'timestamp']


class PictureSerializer(serializers.ModelSerializer):
    """Serialize the URL, contributor, and creation time of a picture."""

    class Meta:
        model = Picture
        fields = ['id', 'image_url', 'name', 'timestamp']

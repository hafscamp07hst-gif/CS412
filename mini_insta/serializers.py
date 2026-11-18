# File: mini_insta/serializers.py
# Description: Convert profiles, posts, and photos to and from JSON data.

from rest_framework import serializers
from .models import Photo, Post, Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serialize the information displayed on a profile page."""

    class Meta:
        model = Profile
        fields = ['id', 'username', 'display_name', 'profile_image_url',
                  'bio_text', 'join_date']


class PostSerializer(serializers.ModelSerializer):
    """Serialize posts and validate new post submissions."""

    class Meta:
        model = Post
        fields = ['id', 'profile', 'timestamp', 'caption']
        read_only_fields = ['profile']


class PhotoSerializer(serializers.ModelSerializer):
    """Serialize each photo's post, image URL, and uploaded file URL."""

    class Meta:
        model = Photo
        fields = ['id', 'post', 'image_url', 'image_file', 'timestamp']

# File: mini_insta/models.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Store profiles, posts, and their photos.

from django.db import models


class Profile(models.Model):
    """Store a user's profile information and join date."""

    # Store the name, photo URL, and biography shown on the profile page.
    username = models.TextField(blank=True)
    display_name = models.TextField(blank=True)
    profile_image_url = models.URLField(blank=True)
    bio_text = models.TextField(blank=True)

    # Set the join date once, when the profile is created.
    join_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the username and display name of this profile."""
        return f'{self.username} ({self.display_name})'

    def get_all_posts(self):
        """Return a QuerySet of posts for this profile, newest first."""
        # Find this profile's posts and sort them by timestamp.
        posts = Post.objects.filter(profile=self).order_by('-timestamp')
        return posts


class Post(models.Model):
    """Store a post associated with one profile."""

    # Link the post to its creator and record when it was saved.
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    # Allow posts without a caption.
    caption = models.TextField(blank=True)

    def __str__(self):
        """Return the string representation of this post's profile."""
        return f'{self.profile}'

    def get_all_photos(self):
        """Return a QuerySet of photos for this post, oldest first."""
        # Find this post's photos and sort them by timestamp.
        photos = Photo.objects.filter(post=self).order_by('timestamp')
        return photos


class Photo(models.Model):
    """Store a photo URL associated with one post."""

    # Link the image to its post and store its public URL and save time.
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the string representation of this photo's post."""
        return f'{self.post}'

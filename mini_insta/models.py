# File: mini_insta/models.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Store profiles, posts, photos, follows, comments, and likes.

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    """Store a user's profile information and join date."""

    # Identify the account that can edit this profile and its posts.
    user = models.ForeignKey(User, on_delete=models.CASCADE)

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

    def get_absolute_url(self):
        """Return the detail URL for this profile after an update."""
        # Use this profile's primary key to return to its detail page.
        return reverse('mini_insta:show_profile', kwargs={'pk': self.pk})

    def get_all_posts(self):
        """Return a QuerySet of posts for this profile, newest first."""
        # Find this profile's posts and sort them by timestamp.
        posts = Post.objects.filter(profile=self).order_by('-timestamp')
        return posts


    def get_followers(self):
        """Return a list of Profiles that follow this profile."""
        # Each matching Follow identifies a subscriber in follower_profile.
        follows = Follow.objects.filter(profile=self)
        followers = []
        for follow in follows:
            followers.append(follow.follower_profile)
        return followers

    def get_num_followers(self):
        """Return the number of profiles following this profile."""
        return len(self.get_followers())

    def get_following(self):
        """Return a list of Profiles that this profile follows."""
        # Each matching Follow identifies a publisher in profile.
        follows = Follow.objects.filter(follower_profile=self)
        following = []
        for follow in follows:
            following.append(follow.profile)
        return following

    def get_num_following(self):
        """Return the number of profiles this profile follows."""
        return len(self.get_following())

    def get_post_feed(self):
        """Return posts by followed profiles, with the newest posts first."""
        # Use the existing subscriptions to select posts for this profile.
        following = self.get_following()
        posts = Post.objects.filter(profile__in=following).order_by('-timestamp')
        return posts


class Post(models.Model):
    """Store a post associated with one profile."""

    # Link the post to its creator and record when it was saved.
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    # Allow posts without a caption.
    caption = models.TextField(blank=True)

    def __str__(self):
        """Return the profile and caption of this post."""
        return f'{self.profile}: {self.caption}'

    def get_all_photos(self):
        """Return a QuerySet of photos for this post, oldest first."""
        # Find this post's photos and sort them by timestamp.
        photos = Photo.objects.filter(post=self).order_by('timestamp')
        return photos

    def get_first_photo(self):
        '''Return the oldest photo for a preview, or None if there are none.'''
        photos = self.get_all_photos()
        if len(photos) > 0:
            return photos[0]
        return None


    def get_all_comments(self):
        """Return this post's comments in the order they were created."""
        # Include only comments attached to this post.
        comments = Comment.objects.filter(post=self).order_by('timestamp')
        return comments

    def get_likes(self):
        """Return a QuerySet of likes associated with this post."""
        # Keep likes for other posts out of this post's count.
        likes = Like.objects.filter(post=self)
        return likes


class Photo(models.Model):
    """Store a photo URL or uploaded image associated with one post."""

    # Keep image_url for photos created before file uploads were added.
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True)
    image_file = models.ImageField(upload_to='mini_insta/', blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return this photo's post and image URL."""
        image_url = self.get_image_url()
        if image_url == '':
            image_url = 'No image'
        return f'Post {self.post.pk}: {image_url}'

    def get_image_url(self):
        """Return the stored URL or uploaded file URL for this photo."""
        # Prefer the existing URL when this photo uses a web image.
        if self.image_url:
            return self.image_url

        # Uploaded photos use the URL provided by Django's file storage.
        if self.image_file:
            return self.image_file.url

        return ''


class Follow(models.Model):
    """Store one profile following another profile."""

    # profile is the publisher; follower_profile is the subscriber.
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                related_name='profile')
    follower_profile = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                         related_name='follower_profile')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the names of the follower and the profile being followed."""
        return f'{self.follower_profile.display_name} follows {self.profile.display_name}'


class Comment(models.Model):
    """Store a profile's comment on a post."""

    # Connect the comment to its post and to the profile that wrote it.
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=False)

    def __str__(self):
        """Return the commenter, post number, and comment text."""
        return f'{self.profile.display_name} on Post {self.post.pk}: {self.text}'


class Like(models.Model):
    """Store a profile's approval of a post."""

    # Connect each like to the post and the profile that liked it.
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the name of the profile and the post it likes."""
        return f'{self.profile.display_name} likes Post {self.post.pk}'

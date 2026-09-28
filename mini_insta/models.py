# File: mini_insta/models.py
# Name: Sung Tae Hwang
# BU Email: sthwang@bu.edu
# Description: Define the profile data stored by the Mini Insta application.

from django.db import models


class Profile(models.Model):
    '''Store a user's name, profile image, biography, and join date.'''

    username = models.TextField(blank=True)
    display_name = models.TextField(blank=True)
    profile_image_url = models.URLField(blank=True)
    bio_text = models.TextField(blank=True)
    join_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        '''Return the username and display name of self, this Profile instance.'''
        return f'{self.username} ({self.display_name})'

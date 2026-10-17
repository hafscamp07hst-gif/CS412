# File: mini_insta/forms.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 10/2/2026
# Description: Collect post captions and updates to profile information.

from django import forms
from .models import Post, Profile


class CreatePostForm(forms.ModelForm):
    """Collect the caption for a new Post."""

    class Meta:
        """Associate the form with Post and expose its caption."""

        # Set the profile in the view instead of asking the user to choose it.
        model = Post
        fields = ['caption']


class UpdateProfileForm(forms.ModelForm):
    """Collect changes to an existing Profile."""

    class Meta:
        """Associate the form with the editable Profile fields."""

        # Keep the username and join date unchanged when editing a profile.
        model = Profile
        fields = ['display_name', 'bio_text', 'profile_image_url']

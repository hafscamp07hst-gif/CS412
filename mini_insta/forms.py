# File: mini_insta/forms.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 10/2/2026
# Description: Collect the caption for a new post.

from django import forms
from .models import Post


class CreatePostForm(forms.ModelForm):
    """Collect the caption for a new Post."""

    class Meta:
        """Associate the form with Post and expose its caption."""

        # Set the profile in the view instead of asking the user to choose it.
        model = Post
        fields = ['caption']

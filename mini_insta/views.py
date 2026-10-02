# File: mini_insta/views.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Display profiles and posts, and create new posts.

from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView
from .forms import CreatePostForm
from .models import Photo, Post, Profile


class ProfileListView(ListView):
    """Display all profiles in the profile list template."""

    # Use profiles as the template's list of Profile records.
    model = Profile
    template_name = 'mini_insta/show_all_profiles.html'
    context_object_name = 'profiles'


class ProfileDetailView(DetailView):
    """Display the profile selected by the URL's primary key."""

    # Make the selected Profile available as profile in the template.
    model = Profile
    template_name = 'mini_insta/show_profile.html'
    context_object_name = 'profile'


class PostDetailView(DetailView):
    """Display the post selected by the URL's primary key."""

    # Make the selected Post available as post in the template.
    model = Post
    template_name = 'mini_insta/show_post.html'
    context_object_name = 'post'


class CreatePostView(CreateView):
    """Create a post and its photo for the profile in the URL."""

    # Use the caption form with the post creation template.
    form_class = CreatePostForm
    template_name = 'mini_insta/create_post_form.html'

    def get_context_data(self, **kwargs):
        """Return context with the profile and values supplied in kwargs."""
        context = super().get_context_data(**kwargs)

        # Find the profile identified by the URL's primary key.
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        context['profile'] = profile
        return context

    def form_valid(self, form):
        """Save form's Post and create its Photo from the submitted URL."""
        # Attach the profile before saving the Post from form.
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        form.instance.profile = profile

        # Save the Post and prepare the redirect to its detail page.
        response = super().form_valid(form)
        image_url = self.request.POST.get('image_url', '').strip()

        # Create a Photo when an image URL was submitted.
        if image_url:
            Photo.objects.create(
                post=self.object,
                image_url=image_url,
            )

        return response

    def get_success_url(self):
        """Return the detail URL of the newly saved Post."""
        return reverse('mini_insta:show_post', kwargs={'pk': self.object.pk})

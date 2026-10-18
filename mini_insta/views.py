# File: mini_insta/views.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Display profiles and connections, and create, update, and delete posts.

from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from .forms import CreatePostForm, UpdatePostForm, UpdateProfileForm
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


class UpdateProfileView(UpdateView):
    """Display and process updates to the profile selected by the URL."""

    # Load the existing profile and use the form's editable fields.
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_insta/update_profile_form.html'
    context_object_name = 'profile'


class PostDetailView(DetailView):
    """Display the post selected by the URL's primary key."""

    # Make the selected Post available as post in the template.
    model = Post
    template_name = 'mini_insta/show_post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        """Return the post and its author for the shared navigation.

        kwargs contains extra context values supplied by the generic view.
        """
        context = super().get_context_data(**kwargs)

        # Use the author's profile for the feed and profile navigation links.
        context['profile'] = self.object.profile
        return context


class CreatePostView(CreateView):
    """Create a post and its uploaded photos for the profile in the URL."""

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
        """Save form's Post and create a Photo for each uploaded file."""
        # Attach the profile before saving the Post from form.
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        form.instance.profile = profile

        # Save the Post and prepare the redirect to its detail page.
        response = super().form_valid(form)

        # The previous URL-based creation is replaced by file uploads.
        # image_url = self.request.POST.get('image_url', '').strip()
        # if image_url:
        #     Photo.objects.create(post=self.object, image_url=image_url)

        # Read all files submitted through the form's files input.
        files = self.request.FILES.getlist('files')

        # Create a separate Photo for each uploaded image.
        for image_file in files:
            photo = Photo(post=self.object, image_file=image_file)
            photo.save()

        return response

    def get_success_url(self):
        """Return the detail URL of the newly saved Post."""
        return reverse('mini_insta:show_post', kwargs={'pk': self.object.pk})


class DeletePostView(DeleteView):
    """Display a confirmation form and delete the selected post."""

    # Select the post using the primary key supplied in the URL.
    model = Post
    template_name = 'mini_insta/delete_post_form.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        """Return the post and its profile for the confirmation template.

        kwargs contains extra context values supplied by the generic view.
        """
        context = super().get_context_data(**kwargs)

        # Include the post and its author for display and the cancel link.
        context['post'] = self.object
        context['profile'] = self.object.profile
        return context

    def get_success_url(self):
        """Return the author's profile URL after the post is deleted."""
        # Return to the profile because the deleted post no longer has a page.
        return reverse('mini_insta:show_profile',
                       kwargs={'pk': self.object.profile.pk})


class UpdatePostView(UpdateView):
    """Display and process changes to the selected post's caption."""

    # Use the existing Post and limit changes to the caption form field.
    model = Post
    form_class = UpdatePostForm
    template_name = 'mini_insta/update_post_form.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        """Return the post and its profile for the update template.

        kwargs contains extra context values supplied by the generic view.
        """
        context = super().get_context_data(**kwargs)

        # Provide the author for the cancel form and shared navigation.
        context['profile'] = self.object.profile
        return context

    def get_success_url(self):
        """Return the detail URL of the updated post."""
        # Display the saved caption on the same post's detail page.
        return reverse('mini_insta:show_post', kwargs={'pk': self.object.pk})


class ShowFollowersDetailView(DetailView):
    """Display the profiles that follow the profile selected by the URL."""

    # Provide the selected profile so the template can retrieve its followers.
    model = Profile
    template_name = 'mini_insta/show_followers.html'
    context_object_name = 'profile'


class ShowFollowingDetailView(DetailView):
    """Display the profiles followed by the profile selected by the URL."""

    # Provide the selected profile so the template can retrieve its subscriptions.
    model = Profile
    template_name = 'mini_insta/show_following.html'
    context_object_name = 'profile'


class ShowFeedView(DetailView):
    """Display the post feed for the profile selected by the URL."""

    # The template uses this profile to retrieve posts by followed profiles.
    model = Profile
    template_name = 'mini_insta/show_feed.html'
    context_object_name = 'profile'


class SearchView(ListView):
    """Search profile information and post captions using a text query."""

    # A query displays results; dispatch displays the form before a search.
    template_name = 'mini_insta/search_results.html'
    context_object_name = 'posts'

    def dispatch(self, request, *args, **kwargs):
        """Display the search form when request has no query parameter.

        args and kwargs contain the URL arguments supplied to the view.
        """
        # Keep the profile from the URL available in both search templates.
        self.profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        if 'query' not in self.request.GET:
            return render(request, 'mini_insta/search.html',
                          {'profile': self.profile})
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return posts whose captions contain the search text."""
        query = self.request.GET.get('query', '')
        return Post.objects.filter(caption__icontains=query).order_by('-timestamp')

    def get_context_data(self, **kwargs):
        """Add the selected profile, query, and matching profiles to context.

        kwargs contains extra context values supplied by the generic view.
        """
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query', '')

        # Combine matches from any of the three profile text fields.
        profiles = (Profile.objects.filter(username__icontains=query)
                    | Profile.objects.filter(display_name__icontains=query)
                    | Profile.objects.filter(bio_text__icontains=query))
        context['profile'] = self.profile
        context['query'] = query
        context['profiles'] = profiles
        # ListView already obtained these posts from get_queryset.
        context['posts'] = self.object_list
        return context

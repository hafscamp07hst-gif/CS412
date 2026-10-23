# File: mini_insta/views.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Register accounts, display profiles, and manage profiles and posts.

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from .forms import (
    CreateCommentForm,
    CreatePostForm,
    CreateProfileForm,
    UpdatePostForm,
    UpdateProfileForm,
)
from .models import Follow, Like, Photo, Post, Profile


class MiniInstaLoginRequiredMixin(LoginRequiredMixin):
    """Send unauthenticated visitors to this application's login page."""

    def get_login_url(self):
        """Return the Mini Insta login URL for protected views."""
        return reverse('mini_insta:login')


class ProfileLoginRequiredMixin(MiniInstaLoginRequiredMixin):
    """Require authentication and locate the signed-in user's profile."""

    def get_user_profile(self):
        """Return the user's first profile, including migrated admin profiles."""
        profile = Profile.objects.filter(user=self.request.user).order_by('pk').first()
        if profile is None:
            raise Http404('This account does not have a profile.')
        return profile


class OwnPostRequiredMixin(MiniInstaLoginRequiredMixin):
    """Limit post changes to posts owned by the authenticated account."""

    def get_queryset(self):
        """Return only posts associated with the signed-in user's profiles."""
        return super().get_queryset().filter(profile__user=self.request.user)


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

    def get_context_data(self, **kwargs):
        """Add whether the signed-in account follows this profile.

        kwargs contains extra context values supplied by the generic view.
        """
        context = super().get_context_data(**kwargs)
        context['is_following'] = False
        if self.request.user.is_authenticated:
            context['is_following'] = Follow.objects.filter(
                profile=self.object,
                follower_profile__user=self.request.user).exists()
        return context


class CreateProfileView(CreateView):
    """Register an account and its profile together, then log the user in."""

    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_insta/create_profile_form.html'

    def get_context_data(self, **kwargs):
        """Include the account form, preserving submitted fields and errors.

        kwargs contains extra context values supplied by the generic view.
        """
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            data = self.request.POST if self.request.method == 'POST' else None
            context['user_form'] = UserCreationForm(data)
        return context

    def form_valid(self, form):
        """Save both validated forms and log in the new account.

        form is the validated CreateProfileForm for the new profile.
        """
        user_form = UserCreationForm(self.request.POST)
        if not user_form.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, user_form=user_form))

        # Save both records together so a profile failure cannot orphan a User.
        with transaction.atomic():
            user = user_form.save()
            form.instance.user = user
            form.instance.username = user.username
            response = super().form_valid(form)

        login(self.request, user,
              backend='django.contrib.auth.backends.ModelBackend')
        return response


class OwnProfileDetailView(ProfileLoginRequiredMixin, ProfileDetailView):
    """Display the signed-in user's own profile without a URL primary key."""

    def get_object(self, queryset=None):
        """Return the current profile; queryset is an unused optional lookup."""
        return self.get_user_profile()


class UpdateProfileView(ProfileLoginRequiredMixin, UpdateView):
    """Display and process updates to the signed-in user's profile."""

    # Load the existing profile and use the form's editable fields.
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_insta/update_profile_form.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Return the current profile; queryset is an unused optional lookup."""
        return self.get_user_profile()


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
        context['liked_post_ids'] = []
        if self.request.user.is_authenticated:
            context['liked_post_ids'] = Like.objects.filter(
                profile__user=self.request.user).values_list('post_id', flat=True)
        return context


class CreatePostView(ProfileLoginRequiredMixin, CreateView):
    """Create a post and uploaded photos for the signed-in user's profile."""

    # Use the caption form with the post creation template.
    form_class = CreatePostForm
    template_name = 'mini_insta/create_post_form.html'

    def get_context_data(self, **kwargs):
        """Return the profile and extra template context.

        kwargs contains extra context values supplied by the generic view.
        """
        context = super().get_context_data(**kwargs)

        context['profile'] = self.get_user_profile()
        return context

    def form_valid(self, form):
        """Save the post and create a Photo for each uploaded file.

        form is the validated CreatePostForm containing the new caption.
        """
        # Attach the profile before saving the Post from form.
        form.instance.profile = self.get_user_profile()

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


class DeletePostView(OwnPostRequiredMixin, DeleteView):
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


class UpdatePostView(OwnPostRequiredMixin, UpdateView):
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


class ShowFeedView(ProfileLoginRequiredMixin, DetailView):
    """Display the post feed for the signed-in user's profile."""

    # The template uses this profile to retrieve posts by followed profiles.
    model = Profile
    template_name = 'mini_insta/show_feed.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Return the current profile; queryset is an unused optional lookup."""
        return self.get_user_profile()

    def get_context_data(self, **kwargs):
        """Add the current account's liked post IDs for the feed buttons.

        kwargs contains extra context values supplied by the generic view.
        """
        context = super().get_context_data(**kwargs)
        context['liked_post_ids'] = Like.objects.filter(
            profile__user=self.request.user).values_list('post_id', flat=True)
        return context


class SearchView(ProfileLoginRequiredMixin, ListView):
    """Search profile information and post captions using a text query."""

    # A query displays results; get displays the form before a search.
    template_name = 'mini_insta/search_results.html'
    context_object_name = 'posts'

    def get(self, request, *args, **kwargs):
        """Display the search form when request has no query parameter.

        request is the incoming HTTP request.
        args and kwargs contain the URL arguments supplied to the view.
        """
        # Authentication runs before this method, even for the empty form.
        self.profile = self.get_user_profile()
        if 'query' not in self.request.GET:
            return render(request, 'mini_insta/search.html',
                          {'profile': self.profile})
        return super().get(request, *args, **kwargs)

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
        context['liked_post_ids'] = Like.objects.filter(
            profile__user=self.request.user).values_list('post_id', flat=True)
        return context


class FollowProfileView(ProfileLoginRequiredMixin, View):
    """Create a follow from the logged-in profile to the target profile."""

    def post(self, request, *args, **kwargs):
        """Follow the profile identified by kwargs['pk'].

        request is the incoming POST; args contains any additional URL arguments.
        """
        actor = self.get_user_profile()
        profile = get_object_or_404(Profile, pk=kwargs['pk'])
        if profile.user_id == request.user.pk:
            return HttpResponseForbidden('You cannot follow your own profile.')
        Follow.objects.get_or_create(profile=profile, follower_profile=actor)
        return redirect('mini_insta:show_profile', pk=profile.pk)


class DeleteFollowView(ProfileLoginRequiredMixin, View):
    """Remove only the logged-in profile's follow of the target profile."""

    def post(self, request, *args, **kwargs):
        """Unfollow the profile identified by kwargs['pk'].

        request is the incoming POST; args contains any additional URL arguments.
        """
        actor = self.get_user_profile()
        profile = get_object_or_404(Profile, pk=kwargs['pk'])
        Follow.objects.filter(profile=profile, follower_profile=actor).delete()
        return redirect('mini_insta:show_profile', pk=profile.pk)


class LikePostView(ProfileLoginRequiredMixin, View):
    """Create a like by the logged-in profile on another user's post."""

    def post(self, request, *args, **kwargs):
        """Like the post identified by kwargs['pk'].

        request is the incoming POST; args contains any additional URL arguments.
        """
        actor = self.get_user_profile()
        post = get_object_or_404(Post, pk=kwargs['pk'])
        if post.profile.user_id == request.user.pk:
            return HttpResponseForbidden('You cannot like your own post.')
        Like.objects.get_or_create(post=post, profile=actor)
        return redirect('mini_insta:show_post', pk=post.pk)


class DeleteLikeView(ProfileLoginRequiredMixin, View):
    """Remove only the logged-in profile's like from the target post."""

    def post(self, request, *args, **kwargs):
        """Unlike the post identified by kwargs['pk'].

        request is the incoming POST; args contains any additional URL arguments.
        """
        actor = self.get_user_profile()
        post = get_object_or_404(Post, pk=kwargs['pk'])
        Like.objects.filter(post=post, profile=actor).delete()
        return redirect('mini_insta:show_post', pk=post.pk)


class CreateCommentView(ProfileLoginRequiredMixin, CreateView):
    """Create a comment as the logged-in profile on the post in the URL."""

    form_class = CreateCommentForm
    template_name = 'mini_insta/create_comment_form.html'

    def get_context_data(self, **kwargs):
        """Add the target post and current profile to the comment form.

        kwargs contains extra context values supplied by the generic view.
        """
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['profile'] = self.get_user_profile()
        return context

    def form_valid(self, form):
        """Attach the author and target before saving the comment.

        form is the validated CreateCommentForm containing the comment text.
        """
        form.instance.profile = self.get_user_profile()
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        """Return the post detail URL after the comment has been saved."""
        return reverse('mini_insta:show_post', kwargs={'pk': self.object.post_id})

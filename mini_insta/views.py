# File: mini_insta/views.py
# Name: Sung Tae Hwang
# BU Email: sthwang@bu.edu
# Description: Display the list of profiles and an individual profile.

from django.views.generic import ListView, DetailView
from .models import Profile


class ProfileListView(ListView):
    '''Display all Profile records with the profile list template.'''

    model = Profile
    template_name = 'mini_insta/show_all_profiles.html'
    context_object_name = 'profiles'


class ProfileDetailView(DetailView):
    '''Display the Profile selected by its primary key in the URL.'''

    model = Profile
    template_name = 'mini_insta/show_profile.html'
    context_object_name = 'profile'

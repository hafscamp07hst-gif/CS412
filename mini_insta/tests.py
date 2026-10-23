# File: mini_insta/tests.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Test Task 1 authentication, ownership, and profile routing.

from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Post, Profile


class AuthenticationTests(TestCase):
    """Check public browsing and protect each user's own data."""

    @classmethod
    def setUpTestData(cls):
        """Create two accounts, profiles, and posts for permission checks."""
        cls.owner = User.objects.create_user('owner', password='test-password')
        cls.other = User.objects.create_user('other', password='test-password')
        cls.profile = Profile.objects.create(
            username='owner', display_name='Owner', user=cls.owner)
        cls.other_profile = Profile.objects.create(
            username='other', display_name='Other', user=cls.other)
        cls.post = Post.objects.create(profile=cls.profile, caption='Original')
        cls.other_post = Post.objects.create(
            profile=cls.other_profile, caption='Other post')

    def test_profile_is_linked_to_user(self):
        """Require the Profile foreign key used to identify its owner."""
        self.assertIn('user', {field.name for field in Profile._meta.fields})
        self.assertEqual(self.profile.user, self.owner)

    def test_public_pages_remain_readable(self):
        """Allow anonymous visitors to read profiles, posts, and connections."""
        urls = [reverse('mini_insta:show_all_profiles')]
        for name in ['show_profile', 'show_followers', 'show_following']:
            urls.append(reverse('mini_insta:' + name,
                                kwargs={'pk': self.profile.pk}))
        urls.append(reverse('mini_insta:show_post', kwargs={'pk': self.post.pk}))
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_anonymous_requests_require_login(self):
        """Require login for every private page and preserve its next URL."""
        urls = ['/mini_insta/profile', '/mini_insta/profile/update',
                '/mini_insta/profile/create_post', '/mini_insta/profile/feed',
                '/mini_insta/profile/search',
                '/mini_insta/profile/search?query=owner',
                reverse('mini_insta:update_post', kwargs={'pk': self.post.pk}),
                reverse('mini_insta:delete_post', kwargs={'pk': self.post.pk})]
        for url in urls:
            for method in ['get', 'post']:
                with self.subTest(url=url, method=method):
                    response = getattr(self.client, method)(url)
                    self.assertEqual(response.status_code, 302)
                    self.assertEqual(parse_qs(urlsplit(response.url).query)
                                     .get('next'), [url])

    def test_private_routes_do_not_take_profile_pk(self):
        """Resolve own-profile actions without selecting another profile."""
        for name, suffix in [('show_own_profile', 'profile'),
                             ('update_profile', 'profile/update'),
                             ('create_post', 'profile/create_post'),
                             ('show_feed', 'profile/feed'),
                             ('search', 'profile/search')]:
            with self.subTest(name=name):
                self.assertEqual(reverse('mini_insta:' + name),
                                 '/mini_insta/' + suffix)

    def test_owner_can_open_private_pages(self):
        """Use the signed-in profile for its own profile, feed, and forms."""
        self.client.force_login(self.owner)
        for suffix in ['profile', 'profile/update', 'profile/create_post',
                       'profile/feed', 'profile/search',
                       'profile/search?query=Other']:
            with self.subTest(suffix=suffix):
                response = self.client.get('/mini_insta/' + suffix)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context['profile'], self.profile)

    def test_owner_can_update_profile_and_create_post(self):
        """Keep profile changes and new posts attached to the signed-in user."""
        self.client.force_login(self.owner)
        response = self.client.post('/mini_insta/profile/update', {
            'display_name': 'Updated', 'bio_text': 'New bio',
            'profile_image_url': '', 'user': self.other.pk})
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.display_name, 'Updated')
        self.assertEqual(self.profile.user, self.owner)
        response = self.client.post('/mini_insta/profile/create_post', {
            'caption': 'New caption', 'profile': self.other_profile.pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.get(caption='New caption').profile,
                         self.profile)

    def test_other_user_cannot_change_posts(self):
        """Reject direct GET and POST access to someone else's post forms."""
        self.client.force_login(self.other)
        for name in ['update_post', 'delete_post']:
            url = reverse('mini_insta:' + name, kwargs={'pk': self.post.pk})
            for method in ['get', 'post']:
                with self.subTest(name=name, method=method):
                    response = getattr(self.client, method)(
                        url, {'caption': 'Unauthorized'})
                    self.assertEqual(response.status_code, 404)
        self.post.refresh_from_db()
        self.assertEqual(self.post.caption, 'Original')

    def test_owner_can_update_and_delete_posts(self):
        """Allow the owner to use both post forms and save their changes."""
        self.client.force_login(self.owner)
        update_url = reverse('mini_insta:update_post',
                             kwargs={'pk': self.post.pk})
        delete_url = reverse('mini_insta:delete_post',
                             kwargs={'pk': self.post.pk})
        self.assertEqual(self.client.get(update_url).status_code, 200)
        self.assertEqual(self.client.get(delete_url).status_code, 200)
        self.assertEqual(self.client.post(update_url,
                         {'caption': 'Changed'}).status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.caption, 'Changed')
        self.assertEqual(self.client.post(delete_url).status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_edit_links_are_visible_only_to_the_owner(self):
        """Hide edit controls from anonymous visitors and other users."""
        profile_url = reverse('mini_insta:show_profile',
                              kwargs={'pk': self.profile.pk})
        post_url = reverse('mini_insta:show_post', kwargs={'pk': self.post.pk})
        for user in [None, self.other, self.owner]:
            if user is not None:
                self.client.force_login(user)
            profile_response = self.client.get(profile_url)
            post_response = self.client.get(post_url)
            if user == self.owner:
                self.assertContains(profile_response, 'Update Profile')
                self.assertContains(post_response, 'Update Post')
                self.assertContains(post_response, 'Delete Post')
            else:
                self.assertNotContains(profile_response, 'Update Profile')
                self.assertNotContains(post_response, 'Update Post')
                self.assertNotContains(post_response, 'Delete Post')

    def test_navigation_uses_current_user(self):
        """Show private navigation for the signed-in user on any public page."""
        response = self.client.get(reverse('mini_insta:show_all_profiles'))
        self.assertNotContains(response, 'Post Feed')
        self.assertNotContains(response, 'Create a new post')
        self.client.force_login(self.owner)
        for url in [reverse('mini_insta:show_all_profiles'),
                    reverse('mini_insta:show_profile',
                            kwargs={'pk': self.other_profile.pk})]:
            response = self.client.get(url)
            self.assertContains(response, 'Logged in as owner')
            self.assertContains(response, 'href="/mini_insta/profile/feed"')
            self.assertContains(response, 'href="/mini_insta/profile"')

    def test_multiple_profiles_do_not_crash_own_pages(self):
        """Select the first profile when an account owns migrated profiles."""
        Profile.objects.create(user=self.owner, username='legacy')
        self.client.force_login(self.owner)
        response = self.client.get('/mini_insta/profile')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], self.profile)

    def test_user_without_profile_gets_not_found(self):
        """Avoid a server error if a logged-in account has no Profile yet."""
        user = User.objects.create_user('no-profile')
        self.client.force_login(user)
        self.assertEqual(self.client.get('/mini_insta/profile').status_code, 404)

    def test_old_private_profile_routes_are_removed(self):
        """Reject the previous URLs that selected a private profile by pk."""
        self.client.force_login(self.other)
        for action in ['update', 'feed', 'search', 'create_post']:
            with self.subTest(action=action):
                self.assertEqual(self.client.get(
                    f'/mini_insta/profile/{self.profile.pk}/{action}').status_code,
                    404)

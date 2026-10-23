# File: mini_insta/tests.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Test authentication, registration, social actions, and comments.

from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Comment, Follow, Like, Post, Profile


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


class LoginLogoutTests(TestCase):
    """Check Mini Insta login, redirects, logout, and navigation."""

    @classmethod
    def setUpTestData(cls):
        """Create an ordinary account and profile for authentication flows."""
        cls.user = User.objects.create_user('login-user', password='test-password')
        cls.profile = Profile.objects.create(user=cls.user, username='login-user')

    def test_login_page_displays_form_and_default_next(self):
        """Show an app-styled login form with a CSRF token and default target."""
        response = self.client.get('/mini_insta/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mini_insta/login.html')
        self.assertTemplateUsed(response, 'mini_insta/base.html')
        for field in ['username', 'password', 'csrfmiddlewaretoken', 'next']:
            self.assertContains(response, 'name="' + field + '"')
        self.assertContains(response, 'name="next" value="/mini_insta/"')

    def test_login_authenticates_and_returns_to_all_profiles(self):
        """Persist the session and choose a valid default after direct login."""
        response = self.client.post('/mini_insta/login/', {
            'username': 'login-user', 'password': 'test-password'})
        self.assertRedirects(response, '/mini_insta/')
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_invalid_credentials_show_errors_without_login(self):
        """Keep the form visible when credentials are incorrect."""
        response = self.client.post('/mini_insta/login/', {
            'username': 'login-user', 'password': 'wrong-password'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_protected_views_use_the_app_login(self):
        """Use Mini Insta login for profile actions and post changes alike."""
        post = Post.objects.create(profile=self.profile)
        paths = ['/mini_insta/profile', '/mini_insta/profile/update',
                 '/mini_insta/profile/feed', '/mini_insta/profile/search',
                 '/mini_insta/profile/create_post',
                 f'/mini_insta/post/{post.pk}/update',
                 f'/mini_insta/post/{post.pk}/delete']
        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(urlsplit(response.url).path, '/mini_insta/login/')
                login_page = self.client.get(response.url)
                self.assertEqual(login_page.status_code, 200)
                self.assertEqual(login_page.context['next'], path)

    def test_login_returns_to_the_requested_page_with_its_query(self):
        """Carry the original search URL through login and show its results."""
        target = '/mini_insta/profile/search?query=login-user'
        response = self.client.get(target)
        login_page = self.client.get(response.url)
        self.assertEqual(login_page.context['next'], target)
        response = self.client.post('/mini_insta/login/', {
            'username': 'login-user', 'password': 'test-password',
            'next': login_page.context['next']})
        self.assertRedirects(response, target)

    def test_login_does_not_redirect_to_external_hosts(self):
        """Fall back to All Profiles if a supplied next target is external."""
        response = self.client.post('/mini_insta/login/', {
            'username': 'login-user', 'password': 'test-password',
            'next': 'https://example.com/elsewhere'})
        self.assertRedirects(response, '/mini_insta/')

    def test_logout_requires_post_and_ends_the_session(self):
        """A GET cannot log out; a POST returns to the app confirmation."""
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/mini_insta/logout/').status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.post('/mini_insta/logout/')
        self.assertRedirects(response, '/mini_insta/logout_confirmation/')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.get('/mini_insta/profile').status_code, 302)

    def test_logout_form_requires_a_valid_csrf_token(self):
        """Accept the navigation form's CSRF token and reject a missing one."""
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        page = client.get('/mini_insta/')
        self.assertContains(page, 'action="/mini_insta/logout/" method="POST"')
        self.assertEqual(client.post('/mini_insta/logout/').status_code, 403)
        self.assertIn('_auth_user_id', client.session)
        response = client.post('/mini_insta/logout/', {
            'csrfmiddlewaretoken': client.cookies['csrftoken'].value})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', client.session)

    def test_confirmation_links_to_mini_insta_login(self):
        """Use an app-styled confirmation page with the correct login link."""
        response = self.client.get('/mini_insta/logout_confirmation/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mini_insta/logged_out.html')
        self.assertTemplateUsed(response, 'mini_insta/base.html')
        self.assertContains(response, 'href="/mini_insta/login/"')
        self.assertNotContains(response, '/admin/login/')

    def test_navigation_changes_after_login(self):
        """Show Login for visitors and My Profile plus Log out for users."""
        response = self.client.get('/mini_insta/')
        self.assertContains(response, 'href="/mini_insta/login/"')
        self.assertNotContains(response, 'action="/mini_insta/logout/"')
        self.client.force_login(self.user)
        response = self.client.get('/mini_insta/')
        self.assertNotContains(response, 'href="/mini_insta/login/"')
        self.assertContains(response, 'href="/mini_insta/profile"')
        self.assertContains(response, 'action="/mini_insta/logout/" method="POST"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')


class RegistrationTests(TestCase):
    """Create matching accounts and profiles without partial registrations."""

    @classmethod
    def setUpTestData(cls):
        """Create an existing account and profile for duplicate-name checks."""
        cls.existing_user = User.objects.create_user(
            'existing', password='Existing-Password!72849')
        cls.existing_profile = Profile.objects.create(
            user=cls.existing_user, username='existing', display_name='Existing')

    def registration_data(self, **changes):
        """Return valid registration fields, overridden by changes."""
        data = {
            'username': 'freshprofile',
            'password1': 'New-Account!72849',
            'password2': 'New-Account!72849',
            'display_name': 'New Person',
            'bio_text': 'A new profile.',
            'profile_image_url': 'https://example.com/profile.png',
        }
        data.update(changes)
        return data

    def test_registration_route(self):
        """Expose the create_profile route requested by the assignment."""
        self.assertEqual(reverse('mini_insta:create_profile'),
                         '/mini_insta/create_profile')

    def test_registration_displays_both_forms_with_one_username(self):
        """Share one username field while collecting both forms' other data."""
        response = self.client.get('/mini_insta/create_profile')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mini_insta/create_profile_form.html')
        self.assertTemplateUsed(response, 'mini_insta/base.html')
        self.assertEqual(set(response.context['form'].fields), {
            'username', 'display_name', 'bio_text', 'profile_image_url'})
        self.assertNotIn('user', response.context['form'].fields)
        self.assertContains(response, 'name="username"', count=1)
        for name in ['password1', 'password2', 'display_name', 'bio_text',
                     'profile_image_url', 'csrfmiddlewaretoken']:
            self.assertContains(response, 'name="' + name + '"')

    def test_registration_saves_matching_names_and_logs_in(self):
        """Create an ordinary account, attach its profile, and log it in."""
        response = self.client.post('/mini_insta/create_profile',
                                    self.registration_data())
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='freshprofile')
        profile = Profile.objects.get(username='freshprofile')
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.display_name, 'New Person')
        self.assertEqual(profile.bio_text, 'A new profile.')
        self.assertEqual(profile.profile_image_url,
                         'https://example.com/profile.png')
        self.assertTrue(user.check_password('New-Account!72849'))
        self.assertFalse(user.is_staff or user.is_superuser)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.assertRedirects(response, profile.get_absolute_url())
        self.assertEqual(self.client.get('/mini_insta/profile/create_post')
                         .status_code, 200)

    def test_registration_cannot_attach_an_existing_account(self):
        """Ignore client-supplied account IDs and privilege fields."""
        response = self.client.post('/mini_insta/create_profile',
            self.registration_data(user=self.existing_user.pk,
                                   is_staff='on', is_superuser='on'))
        self.assertEqual(response.status_code, 302)
        profile = Profile.objects.get(username='freshprofile')
        self.assertNotEqual(profile.user_id, self.existing_user.pk)
        self.assertFalse(profile.user.is_staff or profile.user.is_superuser)

    def test_mismatched_passwords_do_not_create_records(self):
        """Redisplay account errors without saving a valid profile alone."""
        response = self.client.post('/mini_insta/create_profile',
            self.registration_data(password2='Different-Password!72849'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('password2', response.context['user_form'].errors)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.context['form']['display_name'].value(),
                         'New Person')

    def test_registration_uses_the_normalized_account_username(self):
        """Keep both names identical when Django normalizes Unicode input."""
        response = self.client.post('/mini_insta/create_profile',
            self.registration_data(username='ｆｒｅｓｈｐｒｏｆｉｌｅ'))
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='freshprofile')
        self.assertEqual(Profile.objects.get(user=user).username, user.username)

    def test_duplicate_username_does_not_create_another_profile(self):
        """Report an existing login name instead of reusing its account."""
        response = self.client.post('/mini_insta/create_profile',
            self.registration_data(username='existing'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.context['user_form'].errors)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)

    def test_invalid_profile_does_not_create_an_orphan_account(self):
        """Validate the profile before saving the otherwise valid account."""
        response = self.client.post('/mini_insta/create_profile',
            self.registration_data(profile_image_url='invalid-image-url'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile_image_url', response.context['form'].errors)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)

    def test_errors_from_both_forms_are_preserved(self):
        """Bind both forms when an invalid submission needs to be displayed."""
        response = self.client.post('/mini_insta/create_profile',
            self.registration_data(profile_image_url='invalid-image-url',
                                   password2='Different-Password!72849'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].is_bound)
        self.assertTrue(response.context['user_form'].is_bound)
        self.assertIn('profile_image_url', response.context['form'].errors)
        self.assertIn('password2', response.context['user_form'].errors)
        self.assertEqual(User.objects.count(), 1)

    def test_registration_keeps_django_password_validation(self):
        """Keep weak-password checks for new registrations."""
        response = self.client.post('/mini_insta/create_profile',
            self.registration_data(password1='abc123', password2='abc123'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('password2', response.context['user_form'].errors)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)

    def test_registration_requires_csrf_token(self):
        """Reject a missing CSRF token and accept the actual registration form."""
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/mini_insta/create_profile',
                         self.registration_data()).status_code, 403)
        response = client.get('/mini_insta/create_profile')
        self.assertEqual(response.status_code, 200)
        data = self.registration_data(
            csrfmiddlewaretoken=client.cookies['csrftoken'].value)
        self.assertEqual(client.post('/mini_insta/create_profile', data)
                         .status_code, 302)

    def test_registration_link_only_appears_for_visitors(self):
        """Advertise creating a profile only when the visitor is logged out."""
        response = self.client.get('/mini_insta/')
        self.assertContains(response, 'href="/mini_insta/create_profile"')
        self.client.force_login(self.existing_user)
        response = self.client.get('/mini_insta/')
        self.assertNotContains(response, 'href="/mini_insta/create_profile"')


class LikesAndFollowsTests(TestCase):
    """Limit social actions to the signed-in profile and show their state."""

    @classmethod
    def setUpTestData(cls):
        """Create three users, profiles, and posts to test ownership."""
        cls.actor_user = User.objects.create_user('actor')
        cls.other_user = User.objects.create_user('publisher')
        cls.third_user = User.objects.create_user('third')
        cls.actor = Profile.objects.create(user=cls.actor_user, username='actor')
        cls.other = Profile.objects.create(user=cls.other_user, username='publisher')
        cls.third = Profile.objects.create(user=cls.third_user, username='third')
        cls.own_post = Post.objects.create(profile=cls.actor, caption='Own caption')
        cls.other_post = Post.objects.create(profile=cls.other, caption='Other caption')

    def action_paths(self):
        """Return all four social action paths using the other user's objects."""
        return [f'/mini_insta/profile/{self.other.pk}/follow',
                f'/mini_insta/profile/{self.other.pk}/delete_follow',
                f'/mini_insta/post/{self.other_post.pk}/like',
                f'/mini_insta/post/{self.other_post.pk}/delete_like']

    def test_required_social_routes(self):
        """Resolve each of the assignment's four required URL patterns."""
        for name, path, pk in zip(
                ['follow', 'delete_follow', 'like', 'delete_like'],
                self.action_paths(),
                [self.other.pk, self.other.pk,
                 self.other_post.pk, self.other_post.pk]):
            with self.subTest(name=name):
                self.assertEqual(reverse('mini_insta:' + name,
                                         kwargs={'pk': pk}), path)

    def test_anonymous_actions_require_login(self):
        """Redirect anonymous action requests to the app login without writes."""
        for path in self.action_paths():
            for method in ['get', 'post']:
                with self.subTest(path=path, method=method):
                    response = getattr(self.client, method)(path)
                    self.assertEqual(response.status_code, 302)
                    self.assertEqual(urlsplit(response.url).path,
                                     '/mini_insta/login/')
                    self.assertEqual(parse_qs(urlsplit(response.url).query)
                                     .get('next'), [path])
        self.assertEqual(Follow.objects.count(), 0)
        self.assertEqual(Like.objects.count(), 0)

    def test_get_requests_do_not_change_social_data(self):
        """Require a POST rather than mutate data when following a URL."""
        self.client.force_login(self.actor_user)
        Follow.objects.create(profile=self.other, follower_profile=self.actor)
        Like.objects.create(post=self.other_post, profile=self.actor)
        for path in self.action_paths():
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 405)
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(Like.objects.count(), 1)

    def test_follow_is_created_for_current_profile_only_once(self):
        """Ignore spoofed actor IDs and avoid duplicate follows on repeat POSTs."""
        self.client.force_login(self.actor_user)
        path = self.action_paths()[0]
        for attempt in range(2):
            response = self.client.post(path, {
                'follower_profile': self.third.pk, 'profile': self.third.pk})
            self.assertRedirects(response, self.other.get_absolute_url())
        self.assertEqual(Follow.objects.count(), 1)
        self.assertTrue(Follow.objects.filter(
            profile=self.other, follower_profile=self.actor).exists())
        self.assertIn(self.other, self.actor.get_following())
        self.assertIn(self.actor, self.other.get_followers())
        self.assertIn(self.other_post, self.actor.get_post_feed())

    def test_unfollow_only_deletes_current_profiles_follow(self):
        """Keep other followers intact and allow an already-absent unfollow."""
        self.client.force_login(self.actor_user)
        Follow.objects.create(profile=self.other, follower_profile=self.actor)
        other_follow = Follow.objects.create(
            profile=self.other, follower_profile=self.third)
        for attempt in range(2):
            response = self.client.post(self.action_paths()[1], {
                'follower_profile': self.third.pk})
            self.assertRedirects(response, self.other.get_absolute_url())
        self.assertEqual(Follow.objects.count(), 1)
        self.assertTrue(Follow.objects.filter(pk=other_follow.pk).exists())
        self.assertNotIn(self.other_post, self.actor.get_post_feed())

    def test_like_is_created_for_current_profile_only_once(self):
        """Ignore spoofed actor IDs and avoid duplicate likes on repeat POSTs."""
        self.client.force_login(self.actor_user)
        for attempt in range(2):
            response = self.client.post(self.action_paths()[2], {
                'profile': self.third.pk, 'post': self.own_post.pk})
            self.assertRedirects(response, reverse('mini_insta:show_post',
                                 kwargs={'pk': self.other_post.pk}))
        self.assertEqual(Like.objects.count(), 1)
        self.assertTrue(Like.objects.filter(
            post=self.other_post, profile=self.actor).exists())

    def test_unlike_only_deletes_current_profiles_like(self):
        """Keep other likes intact and allow an already-absent unlike."""
        self.client.force_login(self.actor_user)
        Like.objects.create(post=self.other_post, profile=self.actor)
        other_like = Like.objects.create(post=self.other_post, profile=self.third)
        for attempt in range(2):
            response = self.client.post(self.action_paths()[3], {
                'profile': self.third.pk})
            self.assertRedirects(response, reverse('mini_insta:show_post',
                                 kwargs={'pk': self.other_post.pk}))
        self.assertEqual(Like.objects.count(), 1)
        self.assertTrue(Like.objects.filter(pk=other_like.pk).exists())

    def test_following_yourself_and_liking_own_posts_is_forbidden(self):
        """Reject self-actions even when someone posts to their URLs directly."""
        self.client.force_login(self.actor_user)
        for path in [f'/mini_insta/profile/{self.actor.pk}/follow',
                     f'/mini_insta/post/{self.own_post.pk}/like']:
            with self.subTest(path=path):
                self.assertEqual(self.client.post(path).status_code, 403)
        self.assertEqual(Follow.objects.count(), 0)
        self.assertEqual(Like.objects.count(), 0)

    def test_other_profiles_owned_by_same_account_cannot_be_targets(self):
        """Keep the self-action rule consistent for migrated shared accounts."""
        extra = Profile.objects.create(user=self.actor_user, username='legacy')
        extra_post = Post.objects.create(profile=extra)
        self.client.force_login(self.actor_user)
        for path in [f'/mini_insta/profile/{extra.pk}/follow',
                     f'/mini_insta/post/{extra_post.pk}/like']:
            with self.subTest(path=path):
                self.assertEqual(self.client.post(path).status_code, 403)

    def test_missing_targets_return_not_found(self):
        """Reject actions on absent profiles or posts without creating records."""
        self.client.force_login(self.actor_user)
        for path in ['/mini_insta/profile/999999/follow',
                     '/mini_insta/profile/999999/delete_follow',
                     '/mini_insta/post/999999/like',
                     '/mini_insta/post/999999/delete_like']:
            with self.subTest(path=path):
                self.assertEqual(self.client.post(path).status_code, 404)
        self.assertEqual(Follow.objects.count(), 0)
        self.assertEqual(Like.objects.count(), 0)

    def test_accounts_without_profiles_cannot_act(self):
        """Return a normal not-found response when an account has no profile."""
        account = User.objects.create_user('no-social-profile')
        self.client.force_login(account)
        for path in self.action_paths():
            with self.subTest(path=path):
                self.assertEqual(self.client.post(path).status_code, 404)

    def test_social_actions_require_csrf(self):
        """Reject all four missing tokens and accept actual form submissions."""
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.actor_user)
        for path in self.action_paths():
            with self.subTest(path=path):
                self.assertEqual(client.post(path).status_code, 403)
        client.get(self.other.get_absolute_url())
        token = client.cookies['csrftoken'].value
        for path in self.action_paths():
            with self.subTest(path=path):
                self.assertEqual(client.post(path, {'csrfmiddlewaretoken': token})
                                 .status_code, 302)
        self.assertEqual(Follow.objects.count(), 0)
        self.assertEqual(Like.objects.count(), 0)

    def test_follow_button_tracks_relationship_state(self):
        """Switch between Follow and Unfollow on the other profile's page."""
        self.client.force_login(self.actor_user)
        follow, unfollow = self.action_paths()[:2]
        response = self.client.get(self.other.get_absolute_url())
        self.assertContains(response, f'action="{follow}" method="POST"')
        self.assertNotContains(response, f'action="{unfollow}"')
        self.client.post(follow)
        response = self.client.get(self.other.get_absolute_url())
        self.assertContains(response, f'action="{unfollow}" method="POST"')
        self.assertNotContains(response, f'action="{follow}"')
        self.client.post(unfollow)
        response = self.client.get(self.other.get_absolute_url())
        self.assertContains(response, f'action="{follow}" method="POST"')

    def test_like_buttons_work_on_detail_feed_and_search(self):
        """Use the same Like/Unlike state across all existing post displays."""
        self.client.force_login(self.actor_user)
        Follow.objects.create(profile=self.other, follower_profile=self.actor)
        like, unlike = self.action_paths()[2:]
        pages = [reverse('mini_insta:show_post',
                         kwargs={'pk': self.other_post.pk}),
                 '/mini_insta/profile/feed',
                 '/mini_insta/profile/search?query=caption']
        for path in pages:
            with self.subTest(path=path, state='not liked'):
                response = self.client.get(path)
                self.assertContains(response, f'action="{like}" method="POST"')
                self.assertNotContains(response, f'action="{unlike}"')
        self.client.post(like)
        for path in pages:
            with self.subTest(path=path, state='liked'):
                response = self.client.get(path)
                self.assertContains(response, f'action="{unlike}" method="POST"')
                self.assertNotContains(response, f'action="{like}"')
        self.client.post(unlike)
        response = self.client.get(pages[0])
        self.assertContains(response, f'action="{like}" method="POST"')

    def test_anonymous_and_owner_pages_hide_action_controls(self):
        """Keep public browsing readable and hide unavailable social controls."""
        profile_page = self.other.get_absolute_url()
        post_page = reverse('mini_insta:show_post',
                            kwargs={'pk': self.other_post.pk})
        for user in [None, self.other_user]:
            if user is not None:
                self.client.force_login(user)
            for path in [profile_page, post_page]:
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                for action in self.action_paths():
                    self.assertNotContains(response, f'action="{action}"')


class CommentCreationTests(TestCase):
    """Create comments only as the signed-in profile on the requested post."""

    @classmethod
    def setUpTestData(cls):
        """Create a commenter and another author with posts for each account."""
        cls.user = User.objects.create_user('commenter', password='test-password')
        cls.other_user = User.objects.create_user('comment-author')
        cls.profile = Profile.objects.create(user=cls.user, username='commenter')
        cls.other_profile = Profile.objects.create(
            user=cls.other_user, username='comment-author')
        cls.post = Post.objects.create(profile=cls.other_profile, caption='A post')
        cls.own_post = Post.objects.create(profile=cls.profile, caption='Own post')

    def comment_url(self, post=None):
        """Return the creation URL for post, defaulting to the other author's."""
        post = post or self.post
        return f'/mini_insta/post/{post.pk}/create_comment'

    def test_comment_route(self):
        """Resolve the named creation URL to its target post."""
        self.assertEqual(reverse('mini_insta:create_comment',
                                 kwargs={'pk': self.post.pk}), self.comment_url())

    def test_anonymous_comment_requests_require_login(self):
        """Redirect both viewing and submitting the form to Mini Insta login."""
        for method in ['get', 'post']:
            with self.subTest(method=method):
                response = getattr(self.client, method)(
                    self.comment_url(), {'text': 'Anonymous comment'})
                self.assertEqual(response.status_code, 302)
                self.assertEqual(urlsplit(response.url).path, '/mini_insta/login/')
                next_url = parse_qs(urlsplit(response.url).query)['next'][0]
                self.assertEqual(urlsplit(next_url).path, self.comment_url())
        self.assertFalse(Comment.objects.exists())

    def test_authenticated_get_displays_text_form_without_writing(self):
        """Display only editable text and leave author/post assignment to the view."""
        self.client.force_login(self.user)
        response = self.client.get(self.comment_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mini_insta/create_comment_form.html')
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(set(response.context['form'].fields), {'text'})
        self.assertContains(response, 'name="text"')
        self.assertNotContains(response, 'name="profile"')
        self.assertNotContains(response, 'name="post"')
        self.assertFalse(Comment.objects.exists())

    def test_comment_uses_current_profile_and_url_post(self):
        """Ignore spoofed author/target IDs and redirect to the commented post."""
        self.client.force_login(self.user)
        response = self.client.post(self.comment_url(), {
            'text': 'A new comment', 'profile': self.other_profile.pk,
            'post': self.own_post.pk})
        self.assertRedirects(response, reverse('mini_insta:show_post',
                             kwargs={'pk': self.post.pk}))
        comment = Comment.objects.get()
        self.assertEqual(comment.profile, self.profile)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.text, 'A new comment')
        self.assertContains(self.client.get(response.url), 'A new comment')

    def test_users_can_comment_on_their_own_posts(self):
        """Allow own-post discussion, independently of the own-post like rule."""
        self.client.force_login(self.user)
        response = self.client.post(self.comment_url(self.own_post),
                                    {'text': 'My own comment'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.get().post, self.own_post)
        self.assertEqual(Comment.objects.get().profile, self.profile)

    def test_empty_comments_are_rejected_with_errors(self):
        """Reject missing, empty, and whitespace-only text without saving it."""
        self.client.force_login(self.user)
        for data in [{}, {'text': ''}, {'text': '   \n  '}]:
            with self.subTest(data=data):
                response = self.client.post(self.comment_url(), data)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'mini_insta/create_comment_form.html')
                self.assertIn('text', response.context['form'].errors)
                self.assertEqual(response.context['post'], self.post)
        self.assertFalse(Comment.objects.exists())

    def test_missing_post_returns_not_found(self):
        """Handle an absent target for GET, valid POST, and invalid POST."""
        self.client.force_login(self.user)
        path = '/mini_insta/post/999999/create_comment'
        self.assertEqual(self.client.get(path).status_code, 404)
        for data in [{'text': 'A comment'}, {'text': ''}]:
            self.assertEqual(self.client.post(path, data).status_code, 404)
        self.assertFalse(Comment.objects.exists())

    def test_account_without_profile_cannot_comment(self):
        """Handle a logged-in account lacking its Profile without server errors."""
        user = User.objects.create_user('no-comment-profile')
        self.client.force_login(user)
        self.assertEqual(self.client.get(self.comment_url()).status_code, 404)
        self.assertEqual(self.client.post(self.comment_url(),
                         {'text': 'A comment'}).status_code, 404)
        self.assertFalse(Comment.objects.exists())

    def test_comment_requires_valid_csrf_token(self):
        """Reject a missing token, then accept the token in an actual page form."""
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(self.comment_url(),
                         {'text': 'Blocked'}).status_code, 403)
        client.get(reverse('mini_insta:show_post', kwargs={'pk': self.post.pk}))
        response = client.post(self.comment_url(), {
            'text': 'Allowed',
            'csrfmiddlewaretoken': client.cookies['csrftoken'].value})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.get().text, 'Allowed')

    def test_public_post_shows_comments_but_hides_creation_form(self):
        """Keep comments readable while offering the form only after login."""
        Comment.objects.create(profile=self.profile, post=self.post,
                               text='Existing public comment')
        path = reverse('mini_insta:show_post', kwargs={'pk': self.post.pk})
        response = self.client.get(path)
        self.assertContains(response, 'Existing public comment')
        self.assertNotContains(response, f'action="{self.comment_url()}"')
        self.client.force_login(self.user)
        response = self.client.get(path)
        self.assertContains(response,
                            f'action="{self.comment_url()}" method="POST"')

    def test_feed_forms_use_the_correct_posts_and_unique_ids(self):
        """Give each followed post its own form with an unambiguous text label."""
        self.client.force_login(self.user)
        Follow.objects.create(profile=self.other_profile,
                              follower_profile=self.profile)
        second_post = Post.objects.create(profile=self.other_profile)
        response = self.client.get('/mini_insta/profile/feed')
        for post in [self.post, second_post]:
            with self.subTest(post=post.pk):
                self.assertContains(response,
                    f'action="{self.comment_url(post)}" method="POST"')
                self.assertContains(response, f'id="comment-{post.pk}"', count=1)
                self.assertContains(response, f'for="comment-{post.pk}"', count=1)

    def test_comment_html_is_escaped_when_displayed(self):
        """Display submitted HTML as text in both post detail and feed."""
        self.client.force_login(self.user)
        Follow.objects.create(profile=self.other_profile,
                              follower_profile=self.profile)
        text = '<script>alert("comment")</script>'
        response = self.client.post(self.comment_url(), {'text': text})
        self.assertEqual(response.status_code, 302)
        for path in [response.url, '/mini_insta/profile/feed']:
            page = self.client.get(path)
            self.assertNotContains(page, '<script>')
            self.assertContains(page, '&lt;script&gt;')

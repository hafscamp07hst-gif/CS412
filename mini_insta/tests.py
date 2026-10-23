# File: mini_insta/tests.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Test account ownership, authentication, and registration.

from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import User
from django.test import Client, TestCase
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

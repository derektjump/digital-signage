"""Glow's "Try the new look" switch (signage/new_look.py): off for everyone
until a superuser turns it on, and only ever on for superusers."""

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase, override_settings

from signage import kit, new_look
from signage.templatetags.kit_tags import fk_minus


# Tests run without collectstatic, so plain static storage, not the manifest.
@override_settings(STORAGES={**settings.STORAGES, 'staticfiles': {
    'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class NewLookSwitchTests(TestCase):
    databases = {'default', 'data_connect'}

    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser('boss', password='x', first_name='Dee')
        self.staff = User.objects.create_user('mk', password='x', first_name='Mia')

    def page(self, url='/devices/'):
        return self.client.get(url).content.decode()

    def test_off_until_turned_on(self):
        self.client.force_login(self.admin)
        html = self.page()
        self.assertNotIn('look-family', html)
        self.assertNotIn('signage/css/family.css', html)
        self.assertIn('Try the new look', html)

    def test_superuser_turns_it_on_and_off(self):
        self.client.force_login(self.admin)
        r = self.client.post('/new-look/', {'next': '/devices/'})
        self.assertRedirects(r, '/devices/', fetch_redirect_response=False)
        self.assertEqual(r.cookies[new_look.COOKIE].value, '1')
        html = self.page()
        self.assertIn('class="look-family"', html)
        self.assertIn('signage/css/family.css', html)
        self.assertIn('Back to the current look', html)
        # The Grid's sidebar: The Grid on top, Glow's card with Switch app below.
        self.assertIn('THE GRID', html)
        self.assertIn('<b>Glow</b><small>Digital Signage</small>', html)
        self.assertIn('https://the-grid.digital/track/', html)
        # The page's figures sit on the run.
        self.assertIn('fk-run-tile', html)
        r = self.client.post('/new-look/', {'next': '/devices/'})
        self.assertEqual(r.cookies[new_look.COOKIE].value, '')
        self.assertNotIn('look-family', self.page())

    def test_not_for_everyone_yet(self):
        self.client.force_login(self.staff)
        self.client.cookies[new_look.COOKIE] = '1'
        html = self.page()
        self.assertNotIn('look-family', html)
        self.assertNotIn('Try the new look', html)
        self.assertEqual(self.client.post('/new-look/').status_code, 403)

    def test_back_only_to_this_site(self):
        self.client.force_login(self.admin)
        r = self.client.post('/new-look/', {'next': 'https://example.com/'})
        self.assertEqual(r['Location'], '/')

    def test_runs_keep_their_own_paths(self):
        self.assertEqual(kit.run_for('/devices/'), 'wave')
        self.assertEqual(kit.run_for('/'), 'bridge')
        self.assertTrue(kit.run_path(4, 'bridge').startswith('M-40 112'))

    def test_offline_and_inactive_counts(self):
        # These figures used `add:"-"`, which always came out blank.
        self.assertEqual(fk_minus(4, 3), 1)
        self.assertEqual(fk_minus('x', 3), '')

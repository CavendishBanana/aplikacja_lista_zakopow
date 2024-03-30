from django.test import SimpleTestCase
from django.urls import reverse, resolve
from shopping_list.views import index, cookies_policy_view, cancel_invite_to_other_user

class TestURLs(SimpleTestCase):

    def test_main_page_url(self):
        url = reverse("main-page")
        #print("run test main page url to index view flow")
        self.assertEqual( resolve(url).func, index)

    def test_cookies_policy_url(self):
        url = reverse("cookies_policy")
        self.assertEqual(resolve(url).func, cookies_policy_view)

    def test_cancel_invite_url(self):
        url = reverse("cancel_invite", kwargs={"user_profile_url_txt" : "abc-def", "list_id": 10})
        self.assertEqual(resolve(url).func, cancel_invite_to_other_user)


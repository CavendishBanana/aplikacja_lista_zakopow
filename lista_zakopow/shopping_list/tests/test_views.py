from django.test import TestCase, Client
from django.http import HttpResponse
from shopping_list.models import ShoppingList, Product, NormalUser, get_default_user
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from shopping_list.classes.UserInitType import UserInitType
from shopping_list.classes.UserUnified import UserUnified
from shopping_list.views import hash_password
from shopping_list.tests.utils import EnvironmentSetup

import json
from shopping_list.views import get_user_profile_url

class TestViews(TestCase):
    def setUp(self):
        self.login_str ="login2138"
        self.password_str = "!Q2w3e4r5t6y"
        self.email_str = "123@example.com"
        self.login_session_key = "user_login"
        self.nick_str = "nick123"
        self.new_list_name =  "lista z testu automatycznego"
        self.new_product_name = "nowy produkt z testu automatycznego"
        self.list_id = 0
        self.client = Client()

    def __prepare_user_table(self):
        #print("tttttttttttttttttttttttttttttttttttttttttttttttttttttttt")
        users = User.objects.all()
        #for u in users:
        #    print(u.username)
        users_count = len( users )
        if users_count == 0:
            User.objects.create(username="adminuser", password=hash_password("!Q2w3e4r5t6y"), email = "123@example.com")
            users_count += 1
        if users_count == 1:
            User.objects.create(username="defaultuser", password=hash_password("!Q2w3e4r5t6y"), email = "123@example.com")
        #users = User.objects.all()
        #for u in users:
        #    print(u.username)
        #print("tttttttttttttttttttttt  tttttttttttttttttttttttttttt")

    def test_list_main_page_load(self):
        response = self.client.get(reverse("main-page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("shopping_list/index.html")

    def test_register(self):
        env_set_up = EnvironmentSetup()
        env_set_up.prepare_environment()
        data = {"user_login" : self.login_str, "user_email" : self.email_str, 
                "user_password_1" : self.password_str, "user_password_2" : self.password_str, 
                "user_nick" : self.nick_str}
        response = self.client.post( reverse("register_user"), data )
        userrr = UserUnified(self.login_str, UserInitType.LOGIN)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("shopping_list/user_profile.html")
    
    def test_logout(self):
        self.test_register()
        unified_user = UserUnified(self.login_str, UserInitType.LOGIN)
        user_hash = unified_user.invitehash
        data = {"user_hash" : user_hash}
        user_profile_url_txt = get_user_profile_url(unified_user)
        response = self.client.post(reverse("logoutuser", kwargs={"user_profile_url_txt" : user_profile_url_txt}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("shopping_list/index.html")

    def test_login(self):
        self.test_logout()
        response = self.client.post(reverse("login_user"), {"user_login": self.login_str, "user_password_1": self.password_str})
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("shopping_list/user_profile.html")

    def test_create_shopping_list(self):
        self.test_login()
        data = { "new_list_name" : self.new_list_name }
        user_unified = UserUnified(self.login_str, UserInitType.LOGIN)
        user_profile_url = get_user_profile_url(user_unified)
        url = reverse("create_new_list", kwargs={"user_profile_url_txt" : user_profile_url})
        response = self.client.post(url, data)
        list_url = response.__getitem__("Location")
        list_url_contents = list_url.split("/")
        self.list_id = int( list_url_contents[ len(list_url_contents) -1 ] )
        #list_id = int(response.context["list_id"])
        #self.list_id =list_id
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("shopping_list/products_list.html")

    def test_add_item(self):
        self.test_create_shopping_list()
        data={ "new_product_name" : self.new_product_name, "list_id": self.list_id}
        this_user = UserUnified(self.login_str, UserInitType.LOGIN)
        user_profile_url = get_user_profile_url(this_user)
        list_id =self.list_id
        items_in_list_count = len(Product.objects.filter(product_list__id = list_id) )
        response = self.client.post( reverse("add_product", kwargs={ "user_profile_url_txt" : user_profile_url, "list_id" : list_id, }), data  )
        items_in_list_count_2 = len(Product.objects.filter(product_list__id = list_id) )
        self.assertEqual(items_in_list_count + 1, items_in_list_count_2)
        self.assertEqual(response.status_code, 302)   
        self.assertTemplateUsed("shopping_list/products_list.html")

    def test_change_bought_flag(self):
        self.test_add_item()
        user_profile_url = get_user_profile_url( UserUnified(self.login_str, UserInitType.LOGIN) )
        list_id =self.list_id
        url = reverse( "change_added_to_cart", kwargs={"user_profile_url_txt" : user_profile_url, "list_id" : list_id })
        added_item = Product.objects.get(description=self.new_product_name)
        item_bought = added_item.added_to_cart
        data = {"item_id" : added_item.id}
        response = self.client.post(url, data)
        added_item = Product.objects.get(description=self.new_product_name)
        item_bought_flag_after_post = added_item.added_to_cart
        self.assertNotEquals(item_bought, item_bought_flag_after_post)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("shopping_list/products_list.html")

    def test_remove_item(self):
        self.test_add_item()
        user_profile_url = get_user_profile_url( UserUnified(self.login_str, UserInitType.LOGIN) )
        list_id =self.list_id
        url = reverse( "remove_item_from_list", kwargs={"user_profile_url_txt" : user_profile_url, "list_id" : list_id })
        added_items = Product.objects.filter(description=self.new_product_name)
        count_before_remove = len(added_items)
        data = {"item_id" : added_items[0].id}
        response = self.client.post(url, data)
        items_after_remove = Product.objects.filter(description=self.new_product_name).filter(product_list__id=list_id)
        count_after_remove = len(items_after_remove)
        self.assertLess(count_after_remove, count_before_remove)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("shopping_list/products_list.html")






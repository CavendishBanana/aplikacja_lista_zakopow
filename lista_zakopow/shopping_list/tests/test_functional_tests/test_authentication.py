from .utils import get_webdriver, create_n_users, SeleniumTestBase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from shopping_list.classes.UserInitType import UserInitType
from shopping_list.classes.UserUnified import UserUnified
from django.test import Client
from shopping_list.tests.utils import EnvironmentSetup
from django.urls import reverse, resolve
from shopping_list.views import get_user_profile_url
from shopping_list.models import ShoppingList, Product, NormalUser, get_default_user
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

class SeleniumAuthenticationTests(SeleniumTestBase):
    
    def test_selenium_working(self):
        driver = get_webdriver("Chrome")
        self.assertIsNotNone(driver)

    def test_register(self):
        main_page_url = self._get_url("main-page")
        self.driver.get(main_page_url)
        self.driver.maximize_window()
        wait = WebDriverWait(self.driver, 4)
        wait.until(EC.visibility_of_element_located((By.ID, "cookie-consent-button-id")))

        cookie_popup_button_list = self.driver.find_elements(By.ID, "cookie-consent-button-id")
        cookie_popup_button_exists = False
        if len(cookie_popup_button_list) > 0:
            cookie_popup_button_list[0].click()
            cookie_popup_button_exists = True


        register_login_textbox = self.driver.find_elements(By.ID, "user_login_register")
        register_password_1_textbox = self.driver.find_elements(By.ID, "user_password_1_register")
        register_password_2_textbox = self.driver.find_elements(By.ID, "user_password_2_register")
        register_email_textbox = self.driver.find_elements(By.ID, "user_email")
        register_nick_textbox = self.driver.find_elements(By.ID, "user_nick")
        main_page_buttons = self.driver.find_elements(By.XPATH, "//*[@id='user_nick']/ancestor::table//input[@value='zarejestruj']")
        login_textbox_count = len(register_login_textbox)
        pswd_1_textbox_count = len(register_password_1_textbox)
        pswd_2_textbox_count = len(register_password_2_textbox)
        email_textbox_count = len(register_email_textbox)
        nick_textbox_count = len(register_nick_textbox)
        register_buttons_count = len(main_page_buttons)
        
        register_login_textbox[0].send_keys(self.login_str)
        register_email_textbox[0].send_keys(self.email_str)
        register_password_1_textbox[0].send_keys(self.password_str)
        register_password_2_textbox[0].send_keys(self.password_str)
        register_nick_textbox[0].send_keys(self.nick_str)
        main_page_buttons[0].click()
        wait = WebDriverWait(self.driver, 4)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "accountsnippet")))
        account_snippet_div_list = self.driver.find_elements( By.CLASS_NAME ,"accountsnippet")
        account_snippet_count = len(account_snippet_div_list)
        

        cookie_csrf_token = None
        cookie_session_id = None 
        cookie_shopping_list = None

        cookie_csrf_token = self.driver.get_cookie("csrftoken")
        cookie_session_id = self.driver.get_cookie("sessionid")
        cookie_shopping_list = self.driver.get_cookie("lista_zakopow_accept_cookies")

        current_url = self.driver.current_url
        expected_current_user = UserUnified(self.login_str, UserInitType.LOGIN)
        expected_url = self._get_url("user_profile_page", kwargs={"user_profile_url_txt": get_user_profile_url(expected_current_user)} )
        
        self.assertEquals( login_textbox_count , 1)
        self.assertEquals( pswd_1_textbox_count , 1)
        self.assertEquals( pswd_2_textbox_count , 1)
        self.assertEquals( email_textbox_count , 1)
        self.assertEquals( nick_textbox_count , 1)
        self.assertEquals( register_buttons_count , 1)

        self.assertTrue(cookie_popup_button_exists)
        self.assertEquals(account_snippet_count, 1)
        self.assertIsNotNone(cookie_csrf_token)
        self.assertIsNotNone(cookie_session_id)
        self.assertIsNotNone(cookie_shopping_list)
        self.assertEquals(current_url, expected_url)
    
   
    def test_login(self):
        main_page_url = self._get_url("main-page")
        self.driver.get(main_page_url)
        self.driver.maximize_window()
        wait = WebDriverWait(self.driver, 4)
        wait.until(EC.visibility_of_element_located((By.ID, "cookie-consent-button-id")))

        cookie_popup_button_list = self.driver.find_elements(By.ID, "cookie-consent-button-id")
        cookie_popup_button_exists = False
        if len(cookie_popup_button_list) > 0:
            cookie_popup_button_list[0].click()
            cookie_popup_button_exists = True
        
        login_input_list = self.driver.find_elements(By.ID, "user_login_login")
        password_input_list = self.driver.find_elements(By.ID, "user_password_1_login")
        submit_button_list = self.driver.find_elements(By.XPATH, "//*[@id='user_login_login']/ancestor::table//input[@value='zaloguj']")
        
        this_user_credentials = self.users_credentials[0]

        login_input_list[0].send_keys(this_user_credentials["login"])
        password_input_list[0].send_keys(this_user_credentials["password"])
        submit_button_list[0].click()

        wait = WebDriverWait(self.driver, 4)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "accountsnippet")))
        account_snippet_div_list = self.driver.find_elements( By.CLASS_NAME ,"accountsnippet")
        account_snippet_count = len(account_snippet_div_list)
        

        cookie_csrf_token = None
        cookie_session_id = None 
        cookie_shopping_list = None

        cookie_csrf_token = self.driver.get_cookie("csrftoken")
        cookie_session_id = self.driver.get_cookie("sessionid")
        cookie_shopping_list = self.driver.get_cookie("lista_zakopow_accept_cookies")

        current_url = self.driver.current_url
        expected_current_user = UserUnified(this_user_credentials["login"], UserInitType.LOGIN)
        expected_url = self._get_url("user_profile_page", kwargs={"user_profile_url_txt": get_user_profile_url(expected_current_user)} )
        
        self.assertTrue(cookie_popup_button_exists)
        self.assertEquals(account_snippet_count, 1)
        self.assertIsNotNone(cookie_csrf_token)
        self.assertIsNotNone(cookie_session_id)
        self.assertIsNotNone(cookie_shopping_list)
        self.assertEquals(current_url, expected_url)
        self.assertEquals(len(login_input_list), 1)
        self.assertEquals(len(password_input_list), 1)
        self.assertEquals(len(submit_button_list), 1)

    
   

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome import options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from shopping_list.tests.utils import EnvironmentSetup
from django.urls import reverse
from django.test import Client
import os
# from webdriver_manager.chrome import ChromeDriverManager
from os import path
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

def create_n_users(n_users, client, begin_number=0,base_login = "login", base_password = "!Q2w3e4r5t6y", base_email_address="login", base_email_domain="example.com", base_nick="nick"):
        created_users_credentials = []
        for i in range(begin_number, begin_number + n_users):
            i_str = str(i)
            this_user_password = base_password+i_str
            data = {"user_login" : base_login+i_str, "user_email" : base_email_address+i_str+"@"+base_email_domain, 
                    "user_password_1" : this_user_password, "user_password_2" : this_user_password, 
                    "user_nick" : base_nick+i_str}
            client.post( reverse("register_user"), data )
            created_users_credentials.append( {"login" : base_login+i_str, "password" : this_user_password} )
        return created_users_credentials


def build_path(path_elements):
    buffer = ""
    for elem in path_elements:
        buffer = os.path.join(buffer, elem)
    return buffer


def get_webdriver(browser_name, driver_path=""):
    if browser_name == "Chrome":
        return webdriver.Chrome()
            #default_path_elems = ["C:", "Users", "krzys", "OneDrive", "Desktop", "testing_stuff", "webdrivers", "chromedriver", "chromedriver.exe"]
            #path_to_driver = build_path(default_path_elems)
            #if driver_path == "":
            #    driver_path = path_to_driver

            #return webdriver.Chrome(driver_path)
            #service_object = Service()
            #options = webdriver.chrome.options.Options()
            #return webdriver.Chrome(service=service_object, options=options)
            #return webdriver.Chrome()
    elif browser_name == "Edge":
        return webdriver.Edge()
    return None

class SeleniumTestBase(StaticLiveServerTestCase):
    def setUp(self):
        self.login_str ="login2138"
        self.password_str = "!Q2w3e4r5t6y"
        self.email_str = "123@example.com"
        self.login_session_key = "user_login"
        self.nick_str = "nick123"
        self.new_list_name =  "lista z testu automatycznego"
        self.new_product_name = "nowy produkt z testu automatycznego"
        self.list_id = 0
        self.browser_name = "Chrome"
        self.driver = get_webdriver(self.browser_name)
        self.client = Client()
        self.max_wait = 4
        self.domain_name= "127.0.0.1:8000"
        env_set_up = EnvironmentSetup()
        env_set_up.prepare_environment()
        self.users_credentials = create_n_users(3, self.client)

    def _get_url(self, urls_file_url_name, kwargs=None):
        if kwargs is None:
            return self.live_server_url + reverse(urls_file_url_name)
        #return self.domain_name + reverse(urls_file_url_name, kwargs=kwargs)
        return self.live_server_url + reverse(urls_file_url_name, kwargs=kwargs)

    def tearDown(self):
        self.driver.close()

    def _login_user(self, login, password, max_wait=4) -> bool:
        main_page_url = self._get_url("main-page")
        self.driver.get(main_page_url)
        self.driver.maximize_window()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "cookie-consent-button-id")))

        cookie_popup_button_list = self.driver.find_elements(By.ID, "cookie-consent-button-id")
        cookie_popup_button_list[0].click()
        
        login_input_list = self.driver.find_elements(By.ID, "user_login_login")
        password_input_list = self.driver.find_elements(By.ID, "user_password_1_login")
        submit_button_list = self.driver.find_elements(By.XPATH, "//*[@id='user_login_login']/ancestor::table//input[@value='zaloguj']")

        login_input_list[0].send_keys(login)
        password_input_list[0].send_keys(password)
        submit_button_list[0].click()

        wait = WebDriverWait(self.driver, max_wait)
        success_login = True
        try:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "accountsnippet")))
        except:
            success_login = False
        return success_login

    def _get_default_credentials(self):
        return self.users_credentials[0]
    




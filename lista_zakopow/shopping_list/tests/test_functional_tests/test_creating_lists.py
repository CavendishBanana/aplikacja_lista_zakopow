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



class SeleniumCreatingLists(SeleniumTestBase):
    def __login_and_create_new_list(self, user_credentials, new_list_name, login_the_user = True, max_wait = 4):
        user_credentials = self._get_default_credentials()
        textbox_new_list_name, submit_create_new_list = self.__login_and_get_elements_to_create_new_list(user_credentials, login_the_user=login_the_user, max_wait=max_wait)
        textbox_new_list_name.send_keys(new_list_name)
        submit_create_new_list.click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))


    def __login_and_get_elements_to_create_new_list_inside_lists(self, this_user_credentials = None, login_the_user = True, max_wait = 4):
        max_wait = self.max_wait
        if login_the_user:
            if this_user_credentials is not None:
                user_logged_in_flag = self._login_user(this_user_credentials["login"], this_user_credentials["password"], max_wait=max_wait)
            else:
                user_logged_in_flag = self._login_user(self._get_default_credentials["login"], self._get_default_credentials[0]["password"], max_wait=max_wait)
            #new_list_textbox = self.driver.find_elements(By.XPATH, "//form[id='create_new_list_form_id']//input[name='new_list_name']")
        new_list_textbox_list = self.driver.find_elements(By.ID, "new_list_name")
        new_list_submit_list = self.driver.find_elements(By.ID, "create_new_list_button")
        return new_list_textbox_list, new_list_submit_list
    
    def __login_and_get_elements_to_create_new_list(self, this_user_credentials = None, login_the_user = True, max_wait=4):
        textbox_list, submit_list = self.__login_and_get_elements_to_create_new_list_inside_lists(this_user_credentials, login_the_user, max_wait=max_wait)
        return textbox_list[0], submit_list[0]

    def test_create_new_list_ui_elements_present(self):
        this_user_credentials = self.users_credentials[0]
        max_wait=self.max_wait
        new_list_textbox_list, new_list_submit_list = self.__login_and_get_elements_to_create_new_list_inside_lists(this_user_credentials=this_user_credentials, login_the_user=True, max_wait=max_wait)
        self.assertEquals(len(new_list_textbox_list), 1 )
        self.assertEquals(len(new_list_submit_list), 1)

    def __go_back_from_list_page_to_user_profile_page(self, max_wait = 4):
        self.driver.find_element(By.XPATH, "//a[contains(text(), 'powrót')]").click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "accountsnippet")))

    def test_create_new_list_check_record_in_db(self):
        user_credentials = self._get_default_credentials()
        max_wait = self.max_wait
        textbox_new_list_name, submit_create_new_list = self.__login_and_get_elements_to_create_new_list(user_credentials, login_the_user=True, max_wait=max_wait)
        lists_with_matching_name_before = ShoppingList.objects.filter(name = self.new_list_name)
        lists_with_matching_name_count_before = len(lists_with_matching_name_before)
        textbox_new_list_name.send_keys(self.new_list_name)
        submit_create_new_list.click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))
        lists_with_matching_name_after = ShoppingList.objects.filter(name = self.new_list_name)
        lists_with_matching_name_count_after =len(lists_with_matching_name_after)
        self.assertEquals(lists_with_matching_name_count_before + 1, lists_with_matching_name_count_after)


    def test_create_new_list_the_list_is_in_user_profile_ui(self):
        user_credentials = self._get_default_credentials()
        max_wait = self.max_wait

        self._login_user(user_credentials["login"], user_credentials["password"], max_wait)
        my_list_forms_count_before = 0
        lists_with_new_name_count_before = 0
        body_contents = self.driver.find_elements(By.XPATH, "//body/*")

        start_getting_elems = False
        stop_getting_elems = False
        for tag in body_contents:
            if tag.tag_name == "h2" and tag.get_attribute("innerHTML") == "Udostępnione listy":
                stop_getting_elems = True
            if start_getting_elems and not stop_getting_elems and tag.tag_name == "form":
                my_list_forms_count_before += 1
                if tag.find_elements(By.TAG_NAME, "input")[2].get_attribute("value") == self.new_list_name:
                    lists_with_new_name_count_before += 1
            if tag.tag_name == "h2" and tag.get_attribute("innerHTML") == "Moje listy":
                start_getting_elems = True

        self.__login_and_create_new_list(user_credentials, self.new_list_name, False)
        self.__go_back_from_list_page_to_user_profile_page(max_wait)
        
        my_list_forms_count_after = 0
        lists_with_new_name_count_after = 0
        body_contents = self.driver.find_elements(By.XPATH, "//body/*")

        start_getting_elems = False
        stop_getting_elems = False
        for tag in body_contents:
            if tag.tag_name == "h2" and tag.get_attribute("innerHTML") == "Udostępnione listy":
                stop_getting_elems = True
            if start_getting_elems and not stop_getting_elems and tag.tag_name == "form":
                my_list_forms_count_after += 1
                if tag.find_elements(By.TAG_NAME, "input")[2].get_attribute("value") == self.new_list_name:
                    lists_with_new_name_count_after += 1
            if tag.tag_name == "h2" and tag.get_attribute("innerHTML") == "Moje listy":
                start_getting_elems = True

        self.assertEquals(my_list_forms_count_before + 1, my_list_forms_count_after)
        self.assertEquals(lists_with_new_name_count_before + 1, lists_with_new_name_count_after)
        
    def test_create_new_list_new_list_page_ok(self):
        user_credentials = self._get_default_credentials()
        max_wait = self.max_wait
        new_list_name = self.new_list_name
        self._login_user(user_credentials["login"], user_credentials["password"], max_wait)
        self.__login_and_create_new_list(user_credentials, new_list_name, False)
        products_table_rows_count = len(self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr"))

        table_editors = self.driver.find_elements(By.ID, "editing_users_table_id")
        table_editors_count = len(table_editors)
        table_editors = None 

        table_invitees = self.driver.find_elements(By.ID, "invited_users_table_id")
        table_invitees_count = len(table_invitees)
        table_invitees = None 

        p_tag_no_editors_count = len(self.driver.find_elements(By.XPATH, "//p[text()='Nikt nie edytuje twojej listy']"))
        p_tag_no_inviteees_count = len(self.driver.find_elements(By.XPATH, "//p[text()='Nikt nie został zaproszony do edycji listy']"))
        h2_tag__list_name_count = len( self.driver.find_elements(By.XPATH, "//h2[text()='"+new_list_name+"']") )
        account_scippet_count = len( self.driver.find_elements(By.CLASS_NAME, "accountsnippet") )
        this_user = UserUnified(user_credentials["login"], UserInitType.LOGIN)
        this_user_nick_and_hash_in_account_snippet = this_user.nick + " (" + this_user.invitehash + ")"

        td_with_user_nick_and_hash_content = ""
        if account_scippet_count > 0:
            td_with_user_nick_and_hash_content = self.driver.find_element(By.XPATH, "//table[@id='account_snippet_table_id']//tr[2]/td[1]").get_attribute("innerHTML")

        self.assertEquals(products_table_rows_count, 0)
        self.assertEquals(table_editors_count, 0)
        self.assertEquals(table_invitees_count, 0)
        self.assertEquals(p_tag_no_editors_count, 1)
        self.assertEquals(p_tag_no_inviteees_count, 1)
        self.assertEquals(h2_tag__list_name_count, 1)
        self.assertEquals(account_scippet_count, 1)
        self.assertEquals(this_user_nick_and_hash_in_account_snippet, td_with_user_nick_and_hash_content)

    def test_create_list_without_passing_the_name(self):
        user_credentials = self._get_default_credentials()
        max_wait = self.max_wait
        new_list_name = ""
        this_user = UserUnified(user_credentials["login"], UserInitType.LOGIN)
        this_users_lists_count_in_db_count_before = len(ShoppingList.objects.filter(owner = this_user.get_normal_user()))

        my_list_forms_count_before = 0
        lists_with_new_name_count_before = 0
        body_contents = self.driver.find_elements(By.XPATH, "//body/*")

        start_getting_elems = False
        stop_getting_elems = False
        for tag in body_contents:
            if tag.tag_name == "h2" and tag.get_attribute("innerHTML") == "Udostępnione listy":
                stop_getting_elems = True
            if start_getting_elems and not stop_getting_elems and tag.tag_name == "form":
                my_list_forms_count_before += 1
                if tag.find_elements(By.TAG_NAME, "input")[2].get_attribute("value") == new_list_name:
                    lists_with_new_name_count_before += 1
            if tag.tag_name == "h2" and tag.get_attribute("innerHTML") == "Moje listy":
                start_getting_elems = True

        self._login_user(user_credentials["login"], user_credentials["password"], max_wait)
        self.__login_and_create_new_list(user_credentials, new_list_name, False)
        
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "error_popup")))
        
        error_popup_text = self.driver.find_element(By.ID, "error_popup").find_element(By.TAG_NAME, "p").get_attribute("innerHTML")
        expected_error_popup_text = "Podaj nazwę nowej listy"

        current_page_url = self.driver.current_url
        expected_page_url = self._get_url("create_new_list", kwargs={"user_profile_url_txt" : get_user_profile_url(this_user)})

        this_users_lists_count_in_db_count_after = len(ShoppingList.objects.filter(owner = this_user.get_normal_user()))

        lists_with_new_name_count_after = 0
        my_list_forms_count_after = 0
        start_getting_elems = False
        stop_getting_elems = False
        for tag in body_contents:
            if tag.tag_name == "h2" and tag.get_attribute("innerHTML") == "Udostępnione listy":
                stop_getting_elems = True
            if start_getting_elems and not stop_getting_elems and tag.tag_name == "form":
                my_list_forms_count_after += 1
                if tag.find_elements(By.TAG_NAME, "input")[2].get_attribute("value") == new_list_name:
                    lists_with_new_name_count_after += 1
            if tag.tag_name == "h2" and tag.get_attribute("innerHTML") == "Moje listy":
                start_getting_elems = True

        self.assertEquals(this_users_lists_count_in_db_count_before, this_users_lists_count_in_db_count_after)
        self.assertEquals(lists_with_new_name_count_before, lists_with_new_name_count_after)
        self.assertEquals(my_list_forms_count_before, my_list_forms_count_after)
        self.assertEquals(error_popup_text, expected_error_popup_text)
        self.assertEquals(current_page_url, expected_page_url)

    def test_create_list_logged_out(self):
        user_credentials = self._get_default_credentials()
        max_wait = self.max_wait
        new_list_name = self.new_list_name
        self._login_user(user_credentials["login"], user_credentials["password"], max_wait)
        this_user = UserUnified(user_credentials["login"], UserInitType.LOGIN)
        this_user_lists_count_before = len(ShoppingList.objects.filter(owner=this_user.get_normal_user()) )
        user_profile_link = self._get_url( "user_profile_page", kwargs={"user_profile_url_txt" : get_user_profile_url(this_user)})
        self.driver.execute_script("window.open('');") 
        self.driver.switch_to.window(self.driver.window_handles[1]) 
        self.driver.get(user_profile_link) 
        self.driver.switch_to.window(self.driver.window_handles[0]) 
        self.driver.find_element(By.ID, "logout_submit_button_id").click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "error_popup")))
        login_table_count_1st_tab = len(self.driver.find_elements(By.ID, "login-table"))
        login_page_url_1st_tab = self.driver.current_url
        self.driver.switch_to.window(self.driver.window_handles[1]) 
        new_list_name_textbox = self.driver.find_element(By.ID, "new_list_name")
        new_list_create_button = self.driver.find_element(By.ID, "create_new_list_button")
        new_list_name_textbox.send_keys( new_list_name + "_2")
        new_list_create_button.click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "error_popup")))
        login_table_count_2nd_tab = len(self.driver.find_elements(By.ID, "login-table"))
        login_page_url_2nd_tab = self.driver.current_url
        expected_url = self._get_url("main-page")

        this_user_lists_count_after = len(ShoppingList.objects.filter(owner=this_user.get_normal_user()) )

        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0]) 

        self.assertEquals(this_user_lists_count_before, this_user_lists_count_after)
        self.assertEquals(login_table_count_1st_tab, 1)
        self.assertEquals(login_table_count_2nd_tab, 1)
        self.assertEquals(login_page_url_1st_tab, expected_url)
        self.assertEquals(login_page_url_2nd_tab, expected_url)
        




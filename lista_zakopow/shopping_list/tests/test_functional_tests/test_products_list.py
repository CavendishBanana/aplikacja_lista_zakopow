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
from time import sleep

class SeleniumProductsListTest(SeleniumTestBase):
    
    def setUp(self):
        SeleniumTestBase.setUp(self)
        self.not_bought_color = "lightsalmon"
        self.bought_color = "lightgreen"
        self.put_into_cart_text = "włóż do koszyka"
        self.take_out_from_cart_text = "wyjmij z koszyka"
        self.remove_from_list_text = "Usuń"
        self.new_products_default_count = 5

    def __login_and_create_new_list(self, this_user_credentials, new_list_name, max_wait=4):
        self.driver.get( self._get_url( "main-page" ) )
        self.driver.maximize_window()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "user_login_login")))
        cookie_button_list =self.driver.find_elements(By.ID, "cookie-consent-button-id")
        if len(cookie_button_list) > 0:
            cookie_button_list[0].click()
        self.driver.find_element(By.ID, "user_login_login").send_keys( this_user_credentials["login"])
        self.driver.find_element(By.ID, "user_password_1_login").send_keys(this_user_credentials["password"])
        self.driver.find_element(By.XPATH, "//table[@id='login-table']//input[@type='submit']").click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))
        self.driver.find_element(By.ID, "new_list_name").send_keys(new_list_name)
        self.driver.find_element(By.ID, "create_new_list_button").click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))


    def __login_create_list_and_add_products(self, this_user_credentials= None, new_product_base_name = "", new_products_number_appendix_start_from = 0, max_wait = 4, new_list_name="", new_products_count = -1):
        if this_user_credentials is None:
            this_user_credentials = self._get_default_credentials()
            
        this_user = UserUnified(this_user_credentials["login"], UserInitType.LOGIN)
        if new_list_name == "":
            new_list_name = self.new_list_name

        if new_product_base_name == "":
            new_product_base_name = self.new_product_name
        
        if new_products_count == -1:
            new_products_count = self.new_products_default_count
        
        self.__login_and_create_new_list(this_user_credentials, new_list_name, max_wait=max_wait)
        new_products_names = []
        prods_create_count = 0
        for i in range(new_products_number_appendix_start_from, new_products_number_appendix_start_from + new_products_count):
            new_product_name_textbox =self.driver.find_element(By.ID, "new_product_name") 
            new_product_submit_button = self.driver.find_element(By.ID, "add_new_product_button_id")
            new_product_name_textbox.send_keys(new_product_base_name+str(i))
            new_products_names.append(new_product_base_name+str(i))
            new_product_submit_button.click()
            wait = WebDriverWait(self.driver, max_wait)
            wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))
            prods_create_count+=1
        #print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, ",prods_create_count)
        return new_products_names
        
    def test_add_new_products_ui_correct(self):
        #test checking ifnewlycreatedlist has no objects is alreadycreated
        created_products_names = self.__login_create_list_and_add_products()
        products_table_rows = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr")
        new_products_count = self.new_products_default_count
        products_names_correct_in_ui = True 
        all_products_have_not_bought_color = True
        all_products_have_put_into_the_cart_text = True
        for product_row in products_table_rows:
            product_name_td = product_row.find_elements(By.TAG_NAME, "td")[0]
            products_names_correct_in_ui = products_names_correct_in_ui and ( product_name_td.get_attribute("innerHTML") in created_products_names )
            all_products_have_not_bought_color = all_products_have_not_bought_color and ( product_name_td.get_attribute("bgcolor") == self.not_bought_color )
            change_bought_flag_submit = product_row.find_elements(By.TAG_NAME, "input")[2]
            all_products_have_put_into_the_cart_text = all_products_have_put_into_the_cart_text and (change_bought_flag_submit.get_attribute("value") == self.put_into_cart_text )
        
        self.assertEquals(new_products_count, len(products_table_rows))
        self.assertTrue(all_products_have_not_bought_color)
        self.assertTrue(all_products_have_put_into_the_cart_text)
        self.assertTrue(products_names_correct_in_ui)
    
    def test_add_new_products_in_db(self):
        created_products_names = self.__login_create_list_and_add_products()
        products_table_rows = self.driver.find_elements(By.XPATH, "//table[@id=products_table_id]//tr")
        new_products_count = self.new_products_default_count
        this_list_id = int( self.driver.find_element(By.XPATH, "//form[@id='delete_list_form_id']//input[@name='list_id']").get_attribute("value") )
        products_table_rows = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr")
        data_in_rows = []
        for product_row in products_table_rows:
            #print(product_row.get_attribute("innerHTML"))
            product_name = product_row.find_elements(By.TAG_NAME, "td")[0].get_attribute("innerHTML")
            product_bought = ( product_row.find_elements(By.TAG_NAME, "td")[0].get_attribute("bgcolor") == self.bought_color )
            #product_id_str= product_row.find_element(By.XPATH, "//input[@value='" + self.put_into_cart_text + "']/parent::form/input[@name='item_id']" ).get_attribute("value")
            product_id_str = product_row.find_elements(By.TAG_NAME, "input")[1].get_attribute("value")
            product_id = int( product_id_str )
            data_in_rows.append( { "description" : product_name, "bought_flag" : product_bought, "id" : product_id } )
        
        all_products_in_db = True
        all_products_have_correct_values = True
        all_products_are_in_right_shopping_list = True
        data_records_count = 0
        for product_data in data_in_rows:
            products_matching = Product.objects.filter(id = product_data["id"])
            if len(products_matching) == 1:
                all_products_have_correct_values = all_products_have_correct_values and (products_matching[0].description == product_data["description"]) and ( products_matching[0].added_to_cart == product_data["bought_flag"] )
                all_products_are_in_right_shopping_list = all_products_are_in_right_shopping_list and (products_matching[0].product_list.id == this_list_id)
                data_records_count+=1
            else:
                all_products_in_db = False

        self.assertTrue(all_products_in_db)
        self.assertTrue(all_products_have_correct_values)
        self.assertTrue(all_products_are_in_right_shopping_list)
        self.assertEquals(new_products_count,data_records_count)

    def test_change_product_bought_ui(self):
        max_wait = self.max_wait
        created_products_names = self.__login_create_list_and_add_products(new_products_count=1)
        created_product_name = created_products_names[0]
        product_row_contents = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr/*")
        product_color_before = product_row_contents[0].get_attribute("bgcolor")
        change_bought_flag_button =product_row_contents[1].find_element(By.XPATH, "self::node()//input[@type='submit']")
        change_bought_flag_button_text_before = change_bought_flag_button.get_attribute("value")
        product_id_before = product_row_contents[1].find_element(By.XPATH, "//input[@name='item_id']").get_attribute("value")
        products_count_before = len( self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr"))
        product_name_before = product_row_contents[0].get_attribute("innerHTML")
        change_bought_flag_button.click()
        
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))
        
        product_row_contents = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr/*")
        product_color_middle = product_row_contents[0].get_attribute("bgcolor")
        change_bought_flag_button =product_row_contents[1].find_element(By.XPATH, "self::node()//input[@type='submit']")
        change_bought_flag_button_text_middle = change_bought_flag_button.get_attribute("value")
        product_id_middle = product_row_contents[1].find_element(By.XPATH, "//input[@name='item_id']").get_attribute("value")
        products_count_middle = len( self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr"))
        product_name_middle = product_row_contents[0].get_attribute("innerHTML")
        change_bought_flag_button.click()

        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))

        product_row_contents = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr/*")
        product_color_after = product_row_contents[0].get_attribute("bgcolor")
        change_bought_flag_button =product_row_contents[1].find_element(By.XPATH, "self::node()//input[@type='submit']")
        change_bought_flag_button_text_after = change_bought_flag_button.get_attribute("value")
        product_id_after = product_row_contents[1].find_element(By.XPATH, "//input[@name='item_id']").get_attribute("value")
        products_count_after = len( self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr"))
        product_name_after = product_row_contents[0].get_attribute("innerHTML")

        self.assertEquals(product_id_before, product_id_middle)
        self.assertEquals(product_id_middle, product_id_after)

        self.assertEquals(product_color_before, self.not_bought_color)
        self.assertEquals(change_bought_flag_button_text_before, self.put_into_cart_text)
        self.assertEquals(products_count_before, 1)
        self.assertEquals(product_name_before, created_product_name)

        self.assertEquals(product_color_middle, self.bought_color)
        self.assertEquals(change_bought_flag_button_text_middle, self.take_out_from_cart_text)
        self.assertEquals(products_count_middle, 1)
        self.assertEquals(product_name_middle, created_product_name)

        self.assertEquals(product_color_after, self.not_bought_color)
        self.assertEquals(change_bought_flag_button_text_after, self.put_into_cart_text)
        self.assertEquals(products_count_after, 1)
        self.assertEquals(product_name_after, created_product_name)

    def test_change_product_bought_db(self):
        max_wait = self.max_wait
        created_products_names = self.__login_create_list_and_add_products(new_products_count=1)
        created_product_name = created_products_names[0]
        list_id = int( self.driver.find_element(By.XPATH, "//form[@id='delete_list_form_id']//input[@name='list_id']").get_attribute("value") )
        
        products_in_list = Product.objects.filter(product_list__id = list_id)
        created_product = products_in_list[0]
        created_product_description_before = created_product.description
        created_product_in_cart_before = created_product.added_to_cart 
        created_product_shopping_list_id_before = created_product.product_list.id

        product_row_contents = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr/*")
        change_bought_flag_button =product_row_contents[1].find_element(By.XPATH, "self::node()//input[@type='submit']")
        change_bought_flag_button.click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))
        
        products_in_list = Product.objects.filter(product_list__id = list_id)
        created_product = products_in_list[0]
        created_product_description_middle = created_product.description
        created_product_in_cart_middle = created_product.added_to_cart 
        created_product_shopping_list_id_middle = created_product.product_list.id

        product_row_contents = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr/*")
        change_bought_flag_button =product_row_contents[1].find_element(By.XPATH, "self::node()//input[@type='submit']")
        change_bought_flag_button.click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))

        products_in_list = Product.objects.filter(product_list__id = list_id)
        created_product = products_in_list[0]
        created_product_description_after = created_product.description
        created_product_in_cart_after = created_product.added_to_cart 
        created_product_shopping_list_id_after = created_product.product_list.id

        self.assertEquals(created_product_description_before, created_product_name)
        self.assertEquals(created_product_description_middle, created_product_name)
        self.assertEquals(created_product_description_after, created_product_name)
        self.assertEquals(created_product_in_cart_before, False)
        self.assertEquals(created_product_in_cart_middle, True)
        self.assertEquals(created_product_in_cart_after, False )
        self.assertEquals(created_product_shopping_list_id_before, list_id)
        self.assertEquals(created_product_shopping_list_id_middle, list_id)
        self.assertEquals(created_product_shopping_list_id_after, list_id)

    def test_list_products_ui_matches_db(self):
        max_wait = self.max_wait
        created_products_names = self.__login_create_list_and_add_products(new_products_count=1)
        created_product_name = created_products_names[0]
        list_id = int( self.driver.find_element(By.XPATH, "//form[@id='delete_list_form_id']//input[@name='list_id']").get_attribute("value") )

        before_db = {}

        products_in_list = Product.objects.filter(product_list__id = list_id)
        created_product = products_in_list[0]
        before_db["created_product_description"] = created_product.description
        before_db["created_product_in_cart"] = created_product.added_to_cart 
        before_db["created_product_shopping_list_id"] = created_product.product_list.id
        before_db["created_product_id"] = created_product.id

        before_ui = {}

        product_row_contents = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr/*")
        change_bought_flag_button =product_row_contents[1].find_element(By.XPATH, "self::node()//input[@type='submit']")
        before_ui["created_product_description"] = product_row_contents[0].get_attribute("innerHTML")
        before_ui["created_product_in_cart"] = not( change_bought_flag_button.get_attribute("value") == self.put_into_cart_text )
        before_ui["created_product_shopping_list_id"] = list_id
        before_ui["created_product_id"] = int(product_row_contents[1].find_element(By.XPATH, "//input[@name='item_id']").get_attribute("value") )

        change_bought_flag_button.click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))
        list_id = int( self.driver.find_element(By.XPATH, "//form[@id='delete_list_form_id']//input[@name='list_id']").get_attribute("value") )

        middle_db = {}

        products_in_list = Product.objects.filter(product_list__id = list_id)
        created_product = products_in_list[0]
        middle_db["created_product_description"] = created_product.description
        middle_db["created_product_in_cart"] = created_product.added_to_cart 
        middle_db["created_product_shopping_list_id"] = created_product.product_list.id
        middle_db["created_product_id"] = created_product.id

        middle_ui = {}

        product_row_contents = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr/*")
        change_bought_flag_button =product_row_contents[1].find_element(By.XPATH, "self::node()//input[@type='submit']")
        middle_ui["created_product_description"] = product_row_contents[0].get_attribute("innerHTML")
        middle_ui["created_product_in_cart"] = ( change_bought_flag_button.get_attribute("value") == self.take_out_from_cart_text )
        middle_ui["created_product_shopping_list_id"] = list_id
        middle_ui["created_product_id"] = int(product_row_contents[1].find_element(By.XPATH, "//input[@name='item_id']").get_attribute("value") )


        change_bought_flag_button.click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))
        list_id = int( self.driver.find_element(By.XPATH, "//form[@id='delete_list_form_id']//input[@name='list_id']").get_attribute("value") )

        after_db = {}

        products_in_list = Product.objects.filter(product_list__id = list_id)
        created_product = products_in_list[0]
        after_db["created_product_description"] = created_product.description
        after_db["created_product_in_cart"] = created_product.added_to_cart 
        after_db["created_product_shopping_list_id"] = created_product.product_list.id
        after_db["created_product_id"] = created_product.id

        after_ui = {}

        product_row_contents = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr/*")
        change_bought_flag_button =product_row_contents[1].find_element(By.XPATH, "self::node()//input[@type='submit']")
        after_ui["created_product_description"] = product_row_contents[0].get_attribute("innerHTML")
        after_ui["created_product_in_cart"] = not( change_bought_flag_button.get_attribute("value") == self.put_into_cart_text )
        after_ui["created_product_shopping_list_id"] = list_id
        after_ui["created_product_id"] = int(product_row_contents[1].find_element(By.XPATH, "//input[@name='item_id']").get_attribute("value") )

        self.assertDictEqual(before_db, before_ui)
        self.assertDictEqual(middle_db, middle_ui)
        self.assertDictEqual(after_db, after_ui)

    def test_delete_product_ui(self):
        max_wait = self.max_wait
        created_products_names = self.__login_create_list_and_add_products(new_products_count=2)

        product_row_contents = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr/*")
        change_bought_flag_button =product_row_contents[1].find_element(By.XPATH, "self::node()//input[@type='submit']")
        
        change_bought_flag_button.click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))

        list_id_0 = int( self.driver.find_element(By.XPATH, "//form[@id='delete_list_form_id']//input[@name='list_id']").get_attribute("value") )
        product_rows = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr")
        product_rows_count_before_delete =len(product_rows)
        products_id_list = []
        for row in product_rows:
            prod_id = row.find_element(By.XPATH, "self::node()//input[@value='" + self.remove_from_list_text + "']/preceding-sibling::input[@name='item_id']").get_attribute("value")
            products_id_list.append( int(prod_id) )
        
        deleted_prod_id = products_id_list[0]
        product_rows[0].find_element(By.XPATH, "self::node()//input[@value='" + self.remove_from_list_text + "']" ).click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))

        list_id_1 = int( self.driver.find_element(By.XPATH, "//form[@id='delete_list_form_id']//input[@name='list_id']").get_attribute("value") )
        product_rows = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr")
        product_rows_count_after_delete_1 =len(product_rows)
        
        products_id_list_1 = []
        for row in product_rows:
            prod_id = int(row.find_element(By.XPATH, "self::node()//input[@value='" + self.remove_from_list_text + "']/preceding-sibling::input[@name='item_id']").get_attribute("value"))
            products_id_list_1.append(prod_id)
        products_id_list = products_id_list_1
        bought_deleted_item_id_present_after_delete = ( deleted_prod_id in products_id_list )
        deleted_prod_id = products_id_list[0]
        product_rows[0].find_element(By.XPATH, "self::node()//input[@value='" + self.remove_from_list_text + "']" ).click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))

        list_id_2 = int( self.driver.find_element(By.XPATH, "//form[@id='delete_list_form_id']//input[@name='list_id']").get_attribute("value") )
        product_rows = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr")
        product_rows_count_after_delete_2 =len(product_rows)
        products_id_list_1 = []
        for row in product_rows:
            prod_id = int(row.find_element(By.XPATH, "self::node()//input[@value='" + self.remove_from_list_text + "']/preceding-sibling::input[@name='item_id']").get_attribute("value"))
            products_id_list_1.append(prod_id)

        products_id_list = products_id_list_1
        bought_deleted_item_id_present_after_delete_2 = (deleted_prod_id in products_id_list)

        self.assertEquals(list_id_0, list_id_1)
        self.assertEquals(list_id_1, list_id_2)
        self.assertEquals(product_rows_count_after_delete_1 + 1, product_rows_count_before_delete)
        self.assertEquals(product_rows_count_after_delete_2 + 1, product_rows_count_after_delete_1)
        self.assertFalse(bought_deleted_item_id_present_after_delete)
        self.assertFalse(bought_deleted_item_id_present_after_delete_2)

    def test_delete_product_db(self):
        max_wait = self.max_wait
        items_count=2
        created_products_names = self.__login_create_list_and_add_products(new_products_count=items_count)
        list_id = int( self.driver.find_element(By.XPATH, "//form[@id='delete_list_form_id']//input[@name='list_id']").get_attribute("value") )

        product_row_contents = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr/*")
        change_bought_flag_button =product_row_contents[1].find_element(By.XPATH, "self::node()//input[@type='submit']")
        
        change_bought_flag_button.click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))

        product_rows = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr")
        products_id_list = []
        for row in product_rows: 
            prod_id = int(row.find_element(By.XPATH, "self::node()//input[@value='" + self.remove_from_list_text + "']/preceding-sibling::input[@name='item_id']").get_attribute("value"))
            products_id_list.append(prod_id)
        list_products_count_before_delete = len( Product.objects.filter(product_list__id = list_id) )
        item_1_from_ui_to_delete_in_db_before_delete = ( len( Product.objects.filter(id = products_id_list[0] ).filter(product_list__id = list_id) ) > 0)

        product_rows[0].find_element(By.XPATH, "self::node()//input[@value='" + self.remove_from_list_text + "']").click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))

        item_1_deleted_from_db = ( len( Product.objects.filter(id = products_id_list[0] ).filter(product_list__id = list_id) ) == 0)
        list_product_count_after_1st_delete = len( Product.objects.filter(product_list__id = list_id) )

        product_rows = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr")
        products_id_list = []
        for row in product_rows: 
            prod_id = int(row.find_element(By.XPATH, "self::node()//input[@value='" + self.remove_from_list_text + "']/preceding-sibling::input[@name='item_id']").get_attribute("value"))
            products_id_list.append(prod_id)
        
        item_2_from_ui_to_delete_in_db_before_delete = ( len( Product.objects.filter(id = products_id_list[0] ).filter(product_list__id = list_id) ) > 0)
        list_products_count_before_2nd_delete = len( Product.objects.filter(product_list__id = list_id) )

        product_rows[0].find_element(By.XPATH, "self::node()//input[@value='" + self.remove_from_list_text + "']").click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))

        item_2_deleted_from_db = ( len( Product.objects.filter(id = products_id_list[0] ).filter(product_list__id = list_id) ) == 0)
        list_product_count_after_2nd_delete = len( Product.objects.filter(product_list__id = list_id) )

        self.assertTrue(item_1_from_ui_to_delete_in_db_before_delete)
        self.assertTrue(item_1_deleted_from_db)
        self.assertEquals(list_product_count_after_1st_delete + 1, list_products_count_before_delete)
        self.assertTrue(item_2_from_ui_to_delete_in_db_before_delete)
        self.assertTrue(item_2_deleted_from_db)
        self.assertEquals(list_product_count_after_2nd_delete + 1, list_products_count_before_2nd_delete)


    def __prepare_conditions_logged_out_action_on_products_list(self, user_credentials, product_base_name, prod_start_appdx, max_wait, new_list_name, new_products_count):
        max_wait = self.max_wait
        created_products_names = self.__login_create_list_and_add_products(user_credentials, product_base_name, prod_start_appdx, max_wait, new_list_name, new_products_count)

        product_row_contents = self.driver.find_elements(By.XPATH, "//table[@id='products_table_id']//tr/*")
        change_bought_flag_button =product_row_contents[1].find_element(By.XPATH, "self::node()//input[@type='submit']")
        
        change_bought_flag_button.click()
        wait = WebDriverWait(self.driver, max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "logout_submit_button_id")))

        main_page_url = self._get_url("main-page")
        close_tab_after_done = True
        switch_back_to_this_tab = True 
        wait_condition = EC.visibility_of_element_located((By.ID, "page_title_id"))
        
        self._open_another_browser_tab(main_page_url, switch_back_to_this_tab, close_tab_after_done, wait_condition, max_wait, self._logout_user(max_wait))

    def test_product_list_actions_when_logged_out(self):
        user_idx = 0
        list_name_gen = lambda i : (self.new_list_name + str(user_idx) + " logged out")
        new_list_name = list_name_gen(user_idx)
        self.__prepare_conditions_logged_out_action_on_products_list(self.users_credentials[user_idx], self.new_product_name, 0, self.max_wait, new_list_name, 2)
        product_created_after_logout_name = "Product after logging out"
        
        self.driver.find_element(By.ID, "new_product_name" ).send_keys(product_created_after_logout_name)
        self.driver.find_element(By.ID, "add_new_product_button_id").click()
        wait = WebDriverWait(self.driver, self.max_wait)
        wait.until(EC.visibility_of_element_located((By.ID, "page_title_id")))

        expected_url = self._get_url("main-page")
        current_url = self.driver.current_url

        logout_button_located = ( len(self.driver.find_elementd(By.ID, "logout_submit_button_id") ) > 0 )
        main_page_element_located = ( len(self.driver.find_elementd(By.ID, "login-table") ) > 0 )

        this_user = UserUnified(self.users_credentials[user_idx]["login"], UserInitType.LOGIN)
        list_user_was_using = ShoppingList.objects.filter(owner=this_user.get_normal_user()).filter(name = list_name_gen(user_idx))[0]

        product_created =( len( Product.objects.filter(description=product_created_after_logout_name).filter(product_list__id = list_user_was_using.id) ) > 0 )

        self.assertEquals(expected_url, current_url)
        self.assertFalse(logout_button_located)
        self.assertTrue(main_page_element_located)
        self.assertFalse(product_created)

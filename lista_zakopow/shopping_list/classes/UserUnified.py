from django.contrib.auth.models import User 
from  shopping_list.models import NormalUser
#from shopping_list.classes.UserInitType import UserInitType
#from classes.UserInitType import UserInitType
from ..classes.UserInitType import UserInitType
class UserUnified:
    def __init__(self, init_obj, init_type = UserInitType.LOGIN ):
        if init_type == UserInitType.LOGIN:
            self.auth_user = User.objects.get(username = init_obj)
            self.normal_user = self.auth_user.normaluser
        elif init_type == UserInitType.AUTH_USER:
            self.auth_user = init_obj
            self.normal_user = self.auth_user.normaluser
        elif init_type == UserInitType.NORMAL_USER:
            self.normal_user = init_obj
            self.auth_user = init_obj.user
        elif init_type == UserInitType.ID_AUTH_USER:
            self.auth_user  = User.objects.get(id=init_obj)
            self.normal_user = self.auth_user.normaluser
        else:
            self.normal_user = NormalUser.objects.get(id=init_obj)
            self.auth_user = self.normal_user.user
    
    def get_auth_user_id(self):
        return self.auth_user.id

    def get_normal_user(self):
        return self.normal_user
    
    def get_auth_user(self):
        return self.auth_user

    def get_id(self):
        return self.normal_user.id 
    
    id = property(get_id, None)

    def get_login(self):
        return self.auth_user.username 
    
    login = property(get_login, None)

    username = property(get_login, None)

    def get_password(self):
        return self.auth_user.password
    
    def set_password(self, value):
        self.auth_user.password = value
        self.auth_user.save()

    password = property(get_password, set_password)

    def get_email(self):
        return self.auth_user.email
    
    def set_email(self, value):
        self.auth_user.email = value
        self.auth_user.save()

    email = property(get_email, set_email)

    def get_nick(self):
        return self.normal_user.nick
    
    def set_nick(self, value):
        self.normal_user.nick = value
        self.normal_user.save()

    nick = property(get_nick, set_nick)

    def get_invitehash(self):
        return self.normal_user.invitehash
    
    def set_invitehash(self, value):
        self.normal_user.invitehash = value
        self.normal_user.save()

    invitehash = property(get_invitehash, set_invitehash)

    def get_editing_user(self):
        return self.normal_user.editingUser_set
    
    edition_rights = property(get_editing_user, None)

    def get_shopping_lists(self):
        return self.normal_user.shoppingList_set

    def get_new_email(self):
        return self.normal_user.email_change_new_email
    
    def set_new_email(self, value):
        self.normal_user.email_change_new_email = value
        self.normal_user.save()
    
    email_change_new_email = property(get_new_email, set_new_email)

    def get_new_email_url(self):
        return self.normal_user.email_change_url
    
    def set_new_email_url(self, value):
        self.normal_user.email_change_url = value

    email_change_url = property(get_new_email_url, set_new_email_url)

    def get_new_email_valid_to_date(self):
        return self.normal_user.email_change_url_valid_to
    
    def set_new_email_valid_to_date(self, value):
        self.normal_user.email_change_url_valid_to = value

    email_change_url_valid_to = property(get_new_email_valid_to_date, set_new_email_valid_to_date)

    def save_new_email_data(self, new_email, new_email_url, valid_to_date):
        self.normal_user.email_change_new_email = new_email
        self.normal_user.email_change_url = new_email_url
        self.normal_user.email_change_url_valid_to = valid_to_date
        self.normal_user.save()

        
def usersEqual(user1, user2):
    return user1.username == user2.username





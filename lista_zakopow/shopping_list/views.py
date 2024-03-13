from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import View
from django.utils.text import slugify
from django.db.models import Q
from django.db import transaction
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password, PBKDF2PasswordHasher
from . import models
from random import randint
import hashlib
import uuid 
from django.contrib.auth.models import User 
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.utils import timezone
import json

#from shopping_list.classes import UserUnified
#from shopping_list.classes.UserInitType import UserInitType
#from classes import UserUnified
#from classes import UserInitType
from .classes.UserInitType import UserInitType
from .classes.UserUnified import UserUnified, usersEqual

def hashText(text):
    """
        Basic hashing function for a text using random unique salt.  
    """
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + text.encode()).hexdigest() + ':' + salt
    
def matchHashedText(hashedText, providedText):
    """
        Check for the text in the hashed text
    """
    _hashedText, salt = hashedText.split(':')
    return (_hashedText == hashlib.sha256(salt.encode() + providedText.encode()).hexdigest())

def set_change_email_dates():
    all_normal_users = models.NormalUser.objects.all()
    for user in all_normal_users:
        user.email_change_url_valid_to = datetime(2000,1,1,0,0,1)
        user.save()


def index(httprequest):
    defusr = User.objects.get(username = "defaultuser")
    print("index defaultuser username: " + str(defusr.username) +", id: " + str(defusr.id))

    if user_is_logged_in(httprequest):
        matching_user = get_logged_in_user_from_request_obj(httprequest)
        if matching_user is not None:
            #set_change_email_dates()
            user_url = get_user_profile_url(matching_user)
            return HttpResponseRedirect( reverse("user_profile_page", args=(user_url,)))
        httprequest.session.pop("user_login")
        httprequest.session.modified=True
    return render(httprequest, "shopping_list/index.html")


def cookies_policy_view(httprequest):
    return render(httprequest, "shopping_list/cookies_policy.html")


    '''
    if httprequest.method == "GET":
        products_0 = models.Product.objects.all().values()
        products=[]
        print("Products count: "+str(len(products_0)))
        print("Index view function")
        for product in products_0:
            bought_flag = (product["added_to_cart"] == True)
            print("product id: ", str(product["id"]))
            products.append( {"id" : str(product["id"]), "description": str(product["description"]), "bought": bought_flag } )
        return render(httprequest, "shopping_list/index.html", {"products" : products, "products_count": str(len(products))})
    '''
def load_user_profile(httprequest, user_profile_url_txt):
    print("load_user_profile view - method: ", httprequest.method)
    #if httprequest.method == "POST":
    print("load_user_profile view - passed check if method is post")
    if user_is_logged_in(httprequest):
        user = get_logged_in_user_from_request_obj(httprequest)
        if user is not None:
            print("load_user_profile view - passed check if user with user_login exists")
            
            lists_owned = models.ShoppingList.objects.filter(owner=user.get_normal_user())
            lists_being_edited = models.ShoppingList.objects.filter(~Q(owner=user.get_normal_user()) & Q(editor=user.get_normal_user()))
            resp_list_owned = []
            for lst in lists_owned:
                resp_list_owned.append( { "name" : lst.name, "create_date": lst.create_date, "id" : lst.id, "list_link" : reverse("list_page", args=[get_user_profile_url(user), lst.id]) })
            resp_list_edited = []
            for lst in lists_being_edited:
                resp_list_edited.append( { "name" : lst.name, "create_date": lst.create_date, "id": lst.id, "list_link" : reverse("list_page", args=[get_user_profile_url(user), lst.id]) } )
            invites = models.EditingUser.objects.filter(normalUser = user.get_normal_user(), inviteAccepted = False)
            invites_data = []
            for invite in invites:
                inv_shopping_list = invite.shoppingList
                invite_data = { "list_name" : inv_shopping_list.name, "list_id" : inv_shopping_list.id, "list_owner" : inv_shopping_list.owner.nick, "owner_hash" : inv_shopping_list.owner.invitehash }
                invites_data.append(invite_data)
            user_data = { "nick": user.nick, "user_profile_url_txt" : get_user_profile_url(user), "user_hash": user.invitehash}
            print("load_user_profile_view - before render in green path")
            print("session contents")
            for key, value in httprequest.session.items():
                print('{} => {}'.format(key, value))
            return render(httprequest, "shopping_list/user_profile.html", { "owned_lists" : resp_list_owned, "edited_lists": resp_list_edited, "user_data": user_data, "invites_data": invites_data} )
    print("load_user_profile - red path - before redirect to main page")
    return HttpResponseRedirect( reverse("main-page"))


#a

def logout_user(httprequest, user_profile_url_txt):
    print("miau miau miau miau")
    if httprequest.method == "POST":
        print("hrum hrum")
        if user_is_logged_in(httprequest):
            user = get_logged_in_user_from_request_obj(httprequest)
            if user is not None:
                logout(httprequest)
                del httprequest.session
    return HttpResponseRedirect( reverse("main-page"))


def edit_profile(httprequest, user_profile_url_txt):
    if httprequest.method == "GET":
        if user_is_logged_in(httprequest):
            user = get_logged_in_user_from_request_obj(httprequest)
            if user is not None:
                if not "list_id" in httprequest.POST:
                    return render(httprequest, "shopping_list/edit_profile_pane.html", {"user_obj" : user, "user_profile_url_txt" : get_user_profile_url(user)})
                else: 
                    return render(httprequest, "shopping_list/edit_profile_pane.html", {"user_obj" : user, "list_id" : int(httprequest.POST["list_id"]), "user_profile_url_txt" : get_user_profile_url(user)})
    return HttpResponseRedirect( reverse("main-page"))


def update_nick(httprequest, user_profile_url_txt):
    if httprequest.method == "POST":
        if user_is_logged_in(httprequest):
            user = get_logged_in_user_from_request_obj(httprequest)
            if user is not None:
                context = {}
                context["user_profile_url_txt"]= get_user_profile_url(user)
                if "list_id" in httprequest.POST:
                    context["list_id"] = int(httprequest.POST["list_id"])
                new_nick = httprequest.POST["new_nick"]
                new_nick =new_nick.strip()
                confirm_password = httprequest.POST ["confirm_password"]
                if len(new_nick) == 0:
                    context["user_obj"] = user
                    context["error_flag"] = True
                    context["success_flag"] = False 
                    context["error_msg"] = "Nick nie może być pusty"
                    return render(httprequest, "shopping_list/edit_profile_pane.html", context)
                password_matching = check_password(confirm_password, user.password)
                if password_matching:
                    old_nick = user.nick
                    user.nick = new_nick
                    context["user_obj"] = user
                    context["error_flag"] = False
                    context["success_flag"] = True 
                    context["success_msg"] = "Nick " + old_nick + " zminiony na " + new_nick
                    return render(httprequest, "shopping_list/edit_profile_pane.html", context)
                else:
                    context["user_obj"] = user
                    context["error_flag"] = True 
                    context["success_flag"] = False
                    context["error_msg"] = "Niepoprawne hasło"
                    return render(httprequest, "shopping_list/edit_profile_pane.html", context)
    return HttpResponseRedirect( reverse("main-page"))


def update_password(httprequest, user_profile_url_txt):
    if httprequest.method == "POST":
        if user_is_logged_in(httprequest):
            user = get_logged_in_user_from_request_obj(httprequest)
            if user is not None:
                new_password_1 = httprequest.POST["new_password_1"].strip()
                new_password_2 = httprequest.POST["new_password_2"].strip()
                current_password = httprequest.POST["current_password"].strip()
                context = {}
                context["user_profile_url_txt"]= get_user_profile_url(user)
                context["user_obj"] = user
                context["error_flag"] = True 
                context["success_flag"] = False
                if "list_id" in httprequest.POST:
                    context["list_id"] = int(httprequest.POST["list_id"])
                if new_password_1 != new_password_2: 
                    context["error_msg"] = "Podane hasła się różnią"
                    return render(httprequest, "shopping_list/edit_profile_pane.html", context)
                if not my_validate_password(new_password_1):
                    context["error_msg"] = "Hasło nie jest wystarczająco silne - hasło musi mieć min. 8 znaków, posiadać znak specjalny, cyfrę, małe i duże litery i nie być podobne do loginu"
                    return render(httprequest, "shopping_list/edit_profile_pane.html", context)
                if not check_password(current_password, user.password):
                    context["error_msg"] = "Niepoprawne obecne hasło"
                    return render(httprequest, "shopping_list/edit_profile_pane.html", context)
                if current_password == new_password_1:
                    context["error_msg"] = "Hasło jest takie samo jak stare hasło"
                    return render(httprequest, "shopping_list/edit_profile_pane.html", context)
                hashed_password = hash_password(new_password_1)
                user.password = hashed_password
                #user_login = user.login
                #logout(httprequest)
                #user = authenticate(httprequest, username= user_login, password=new_password_1)
                #login(httprequest, user)
                #user = UserUnified(user, UserInitType.AUTH_USER)
                update_session_auth_hash(httprequest, user.get_auth_user())
                context["error_flag"] = False
                context["success_flag"] = True
                context["success_msg"] = "Hasło zostało zmienione"
                return render(httprequest, "shopping_list/edit_profile_pane.html", context)
            r = HttpResponseRedirect( reverse("main-page"))
    return HttpResponseRedirect( reverse("main-page"))


def save_data_for_new_email_confirmation(unified_user, new_email):
    text_to_hash = unified_user.nick+unified_user.invitehash+str(randint(0, 2147483640))
    hashed_text = hashText(text_to_hash)
    hashed_text = hashed_text[:30]
    old_url = unified_user.email_change_url
    while old_url == hashed_text:
        text_to_hash = unified_user.nick+unified_user.invitehash+str(randint(0, 2147483640))+hashed_text
        hashed_text = hashText(text_to_hash)
        hashed_text, salt = hashed_text.split(":")
        hashed_text = hashed_text[:30]
    
    one_hour_later = datetime.now() + timedelta(hours=1)
    unified_user.save_new_email_data(new_email, hashed_text, one_hour_later)

def get_email_to_send_email_change_confirmations():
    user = User.objects.get(id=2)
    return str(user.email)


def update_email(httprequest, user_profile_url_txt):
    #TODO add logic to the project that sends confirmation email to the user and updates email only after reciving confirmation from email
    if httprequest.method == "POST":
        if user_is_logged_in(httprequest):
            user = get_logged_in_user_from_request_obj(httprequest)
            if user is not None:
                new_email = httprequest.POST["new_email"].strip()
                confirm_password = httprequest.POST["confirm_password"].strip()
                context = {}
                context["user_profile_url_txt"]= get_user_profile_url(user)
                if "list_id" in httprequest.POST:
                    context["list_id"] =int( httprequest.POST["list_id"] )
                context["user_obj"] = user
                context["error_flag"] = True 
                context["success_flag"] = False
                if len(new_email) == 0:
                    context["error_msg"] = "Podaj nowy adres email"
                    return render(httprequest, "shopping_list/edit_profile_pane.html", context)
                if not check_password(confirm_password, user.password):
                    context["error_msg"] = "Niepoprawne hasło"
                    return render(httprequest, "shopping_list/edit_profile_pane.html", context)
                if user == new_email:
                    context["error_msg"] = "Nowy adres email jest taki sam jak stary"
                    return render(httprequest, "shopping_list/edit_profile_pane.html", context)
                save_data_for_new_email_confirmation(user, new_email)
                message_text = "Na koncie użytkownika " + user.nick + " (hash: "+ user.invitehash +") dokonanano zmiany adresu email. By zakończyć proces zmiany adresu email odwiedź poniższy link: " + reverse("update_email_confirm", kwargs={ "user_profile_url_txt" : get_user_profile_url(user), "change_email_url" : user.email_change_url }) +". Link będzie aktywny do "+str(user.email_change_url_valid_to)+". Jeżeli nie zmieniałeś adresu email, to zignoruj wiadomość. Pozdrawiamy, Zespół Lista zakupów"
                send_mail("Lista zakupów --- potwierdź zmianę adresu email", message_text, get_email_to_send_email_change_confirmations(), [new_email], True )
                context["error_flag"] = False
                context["success_flag"] = True
                context["success_msg"] = "Na nowy adres email wysłana została wiadomość z linkiem potwierdzającym. Link będzie aktywny przez godzinę. Potwierdź zmianę adresu email otwierając ten link."
                return render(httprequest, "shopping_list/edit_profile_pane.html", context)
    return HttpResponseRedirect( reverse("main-page"))


def update_email_confirm(httprequest, user_profile_url_txt, change_email_url):
    if httprequest.method == "GET":
        if user_is_logged_in(httprequest):
            user = get_logged_in_user_from_request_obj(httprequest)
            if user is not None:
                tz_now = timezone.now()
                if user.email_change_url == change_email_url and tz_now < user.email_change_url_valid_to:
                    user.email = user.email_change_new_email
                    return HttpResponseRedirect( reverse("user_profile_page", kwargs = {"user_profile_url_txt": get_user_profile_url(user) }) )
        else: 
            return render(httprequest, "shopping_list/login_email_change.html", {"user_profile_url_txt" : user_profile_url_txt, "change_email_url" : change_email_url})
    return HttpResponseRedirect( reverse("main-page"))


def delete_account(httprequest, user_profile_url_txt):
    if httprequest.method == "POST":
        if user_is_logged_in(httprequest):
            user = get_logged_in_user_from_request_obj(httprequest)
            if user is not None:
                confirm_password = httprequest.POST["confirm_password"].strip()
                context = {}
                context["user_profile_url_txt"]= get_user_profile_url(user)
                if "list_id" in httprequest.POST:
                    context["list_id"] =int( httprequest.POST["list_id"] )
                context["user_obj"] = user
                context["error_flag"] = True 
                context["success_flag"] = False
                if not check_password(confirm_password, user.password):
                    context["error_msg"] = "Niepoprawne hasło"
                    return render(httprequest, "shopping_list/edit_profile_pane.html", context)
                logout(httprequest)
                user.get_auth_user().delete()
    return HttpResponseRedirect( reverse("main-page"))


def create_new_list(httprequest, user_profile_url_txt):
    if httprequest.method == "POST":
        if user_is_logged_in(httprequest):
            matching_user = get_logged_in_user_from_request_obj(httprequest)
            if matching_user is not None:
                new_list_name = httprequest.POST["new_list_name"]
                if len(new_list_name.strip()) > 0:
                    with transaction.atomic():
                        new_list = models.ShoppingList(name=new_list_name, owner=matching_user.get_normal_user())
                        new_list.save()
                        editionRight = models.EditingUser(normalUser = matching_user.get_normal_user(), shoppingList = new_list, inviteAccepted=True)
                        editionRight.save() 
                        list_id = new_list.id
                else:
                    return render(httprequest, "shopping_list/user_profile.html", {"error_flag":True, "error_msg": "Podaj nazwę nowej listy"})
                return HttpResponseRedirect(reverse("list_page", kwargs={ "user_profile_url_txt" : get_user_profile_url(matching_user), "list_id" : list_id }))
    return HttpResponseRedirect( reverse("main-page"))


def list_view(httprequest, user_profile_url_txt, list_id):
    error_data = { "error_flag" : False, "error_msg" : ""}
    if "error_flag" in httprequest.session and httprequest.session["error_flag"] == True:
        error_data["error_flag"] = True
        error_data["error_msg"] = httprequest.session["error_msg"]
        httprequest.session["error_flag"] = False
        httprequest.session["error_msg"] = ""
    if httprequest.method == "GET":
        if user_is_logged_in(httprequest):
            matching_user = get_logged_in_user_from_request_obj(httprequest)
            user_login = matching_user.login
            if matching_user is not None:  
                list_id = int(list_id)
                shopping_list_list = models.ShoppingList.objects.filter(id=list_id)
                shopping_list = shopping_list_list[0]
                list_owner = shopping_list.owner
                list_editors = models.EditingUser.objects.filter(shoppingList=shopping_list).filter(~Q(normalUser=list_owner)).filter(inviteAccepted=True)
                user_is_authorized_to_edit = False
                #i = 0
                for editor_tmp in list_editors:
                    editor = editor_tmp.normalUser
                    if user_login == editor.login and editor_tmp.inviteAccepted == True:
                
                        user_is_authorized_to_edit = True
                        break
                    #i=i+1
                #del list_editors[i]
                user_is_owner = usersEqual(matching_user, list_owner)
                user_is_authorized_to_edit = ( user_is_authorized_to_edit or user_is_owner )

                invites_by_that_user = models.EditingUser.objects.filter(shoppingList = shopping_list).filter(inviteAccepted=False).filter(~Q(normalUser=list_owner))
                invitees_by_that_user = []
                for inv in invites_by_that_user:
                    invitees_by_that_user.append(inv.normalUser)
                if user_is_authorized_to_edit:
                    shoping_list_items_0 = shopping_list.listproducts.all()
                    shopping_list_items = []
                    for item in shoping_list_items_0:
                        shopping_list_items.append( { "id" : item.id, "item_description" : item.description, "in_cart" : (item.added_to_cart == True) } )
                    
                    
                    rendered_response = render(httprequest, "shopping_list/products_list.html", { "products" : shopping_list_items, "is_owner": user_is_owner, "list_name": shopping_list.name, \
                                                                                    "create_date" : shopping_list.create_date, "owner_nick" :  list_owner.nick, \
                                                                                        "add_new_url" : reverse( "add_product", kwargs={ "user_profile_url_txt": get_user_profile_url(matching_user), "list_id": list_id  } ),\
                                                                                        "list_id":list_id, "user_profile_url_txt" : get_user_profile_url(matching_user) , "user_nick": matching_user.nick, "user_hash": matching_user.invitehash , \
                                                                                            "editors" : list_editors, "invitees": invitees_by_that_user, "error_data" : error_data })
                    print("list_view api url: ",reverse("get_products", kwargs={"user_profile_url_txt" : get_user_profile_url(matching_user), "list_id": int(list_id)} ))
                    rendered_response.set_cookie("referesh_link_lista_zakopow", get_api_products_url(kwargs={"user_profile_url_txt" : get_user_profile_url(matching_user), "list_id": int(list_id)} ), None)
                    return rendered_response
                user_url = get_user_profile_url(matching_user)
                return HttpResponseRedirect( reverse("user_profile_page", args=(user_url,))) 
    return HttpResponseRedirect( reverse("main-page"))


def get_api_products_url(kwargs):
    return "127.0.0.1:8000" + reverse("get_products", kwargs = {"user_profile_url_txt" : kwargs["user_profile_url_txt"], "list_id": kwargs["list_id"]} )

def get_products_view(httprequest, user_profile_url_txt, list_id):
    print("get_products_view - enter the function")
    if httprequest.method == "GET":
        if user_is_logged_in(httprequest):
            matching_user = get_logged_in_user_from_request_obj(httprequest)
            user_login = matching_user.login
            if matching_user is not None:  
                list_id = int(list_id)
                shopping_list_list = models.ShoppingList.objects.filter(id=list_id)
                shopping_list = shopping_list_list[0]
                shopping_list_items_0 = shopping_list.listproducts.all()
                shopping_list_items = []
                for item in shopping_list_items_0:
                    shopping_list_items.append( { "id" : item.id, "item_description" : item.description, "in_cart" : (item.added_to_cart == True) } )
                response_data = {"items" : shopping_list_items, "status" : "ok"}
                response_data_json = json.dumps(response_data)
                return HttpResponse(response_data_json)
    return HttpResponse( json.dumps( {"items" : [], "status": "fail"}))


def remove_editor(httprequest, user_profile_url_txt, list_id):
    if httprequest.method == "POST":
        print("remove_editor - 1st if - method is POST")
        if user_is_logged_in(httprequest):
            matching_user = get_logged_in_user_from_request_obj(httprequest)
            if matching_user is not None:
                list_to_remove_editor = models.ShoppingList.objects.get(id = int( httprequest.POST["list_id"]))
                if matching_user.login == list_to_remove_editor.owner.login:
                    editor_to_remove_id = int(httprequest.POST["editor_id"])
                    if editor_to_remove_id != matching_user.id:
                        editron_to_remove = models.NormalUser.objects.get(id=editor_to_remove_id)
                        list_to_have_editron_removed = models.ShoppingList.objects.get(id=list_to_remove_editor)
                        edition_right = models.EditingUser.objects.get(normalUser=editron_to_remove, shoppingList = list_to_have_editron_removed)
                        edition_right.delete()
                        return HttpResponseRedirect( reverse("list_page", kwargs={ "user_profile_url_txt" : get_user_profile_url(matching_user), "list_id": list_to_have_editron_removed.id }) )
    return HttpResponseRedirect( reverse("main-page"))


def invite_editor(httprequest, user_profile_url_txt, list_id):
    if httprequest.method == "POST":
        print("invite_editor - 1st if - method is POST")
        if user_is_logged_in(httprequest):
            matching_user = get_logged_in_user_from_request_obj(httprequest)
            if matching_user is not None:
                list_to_invite_to = models.ShoppingList.objects.get(id = int( httprequest.POST["list_id"] ))
                if matching_user.login == list_to_invite_to.owner.login:
                    invited_hash = httprequest.POST["invited_user_hash"]
                    invited_user_list = models.NormalUser.objects.filter(invitehash=invited_hash)
                    if len(invited_user_list) > 0:
                        invited_user = invited_user_list[0]
                        invite_from_before = models.EditingUser.objects.filter(normalUser = invited_user, shoppingList = list_to_invite_to)
                        if len(invite_from_before) == 0:
                            editing_right_invite = models.EditingUser(normalUser = invited_user, shoppingList = list_to_invite_to)
                            editing_right_invite.save()
                        else:
                            httprequest.session["error_flag"] = True
                            httprequest.session["error_msg"] = "Zaproszenie zostało już wykonane"
                    else:
                        httprequest.session["error_flag"] = True
                        httprequest.session["error_msg"] = "Użytkownik o takim hashu nie istnieje"
                    return HttpResponseRedirect( reverse("list_page", kwargs={ "user_profile_url_txt" : get_user_profile_url(matching_user), "list_id": list_to_invite_to.id }) )

    return HttpResponseRedirect("main-page")


def accept_invite(httprequest, user_profile_url_txt):
    if httprequest.method == "POST":
        print("accept_invite - 1st if - method is POST")
        if user_is_logged_in(httprequest):
            matching_user = get_logged_in_user_from_request_obj(httprequest)
            if matching_user is not None:
                list_invited_to = models.ShoppingList.objects.get(id = int( httprequest.POST["list_id"] ))
                edition_right = models.EditingUser.objects.get(normalUser = matching_user.get_normal_user(), shoppingList = list_invited_to)
                edition_right.inviteAccepted = True
                edition_right.save()
                return HttpResponseRedirect( reverse("user_profile_page", kwargs={ "user_profile_url_txt" : get_user_profile_url(matching_user)}))
    return HttpResponseRedirect(reverse("main-page"))


def cancel_invite_to_other_user(httprequest, user_profile_url_txt, list_id):
    if httprequest.method == "POST":
        if user_is_logged_in(httprequest):
            matching_user = get_logged_in_user_from_request_obj(httprequest)
            if matching_user is not None:
                invitee_hash = httprequest.POST["user_hash"]
                list_id = int(httprequest.POST["list_id"])
                invitee = models.NormalUser.objects.get(invitehash = invitee_hash)
                invitee = UserUnified(invitee, UserInitType.NORMAL_USER)
                if not usersEqual(matching_user, invitee):
                    matching_invites = models.EditingUser.objects.filter(shoppingList = list_id, normalUser = invitee.get_normal_user())
                    if len(matching_invites) > 0:
                        invite = matching_invites[0]
                        if usersEqual(matching_user, invite.shoppingList.owner):
                            invite.delete()
                            return HttpResponseRedirect( reverse("user_profile_page", kwargs={ "user_profile_url_txt" : get_user_profile_url(matching_user)}))
    return HttpResponseRedirect(reverse("main-page"))


def reject_invite(httprequest, user_profile_url_txt):
    if httprequest.method == "POST":
        print("accept_invite - 1st if - method is POST")
        if user_is_logged_in(httprequest):
            matching_user = get_logged_in_user_from_request_obj(httprequest)
            if matching_user is not None:
                list_invited_to = models.ShoppingList.objects.get(id = int( httprequest.POST["list_id"] ))
                if not usersEqual(matching_user, list_invited_to.owner):
                    edition_right = models.EditingUser.objects.get(normalUser = matching_user.get_normal_user(), shoppingList = list_invited_to)
                    edition_right.delete()
                    return HttpResponseRedirect( reverse("list_page", kwargs={ "user_profile_url_txt" : get_user_profile_url(matching_user), "list_id": list_invited_to.id }) )
    return HttpResponseRedirect(reverse("main-page"))


def leave_list_of_other_user(httprequest, user_profile_url_txt, list_id):
    return reject_invite(httprequest, user_profile_url_txt)


def add_product(httprequest, user_profile_url_txt, list_id):
    if httprequest.method == "POST":
        print("add_product - 1st if - method is POST")
        if user_is_logged_in(httprequest):
            matching_user = get_logged_in_user_from_request_obj(httprequest)
            if matching_user is not None:
                print("add_product - user matched")
                product_description = httprequest.POST["new_product_name"]
                list_to_add_to = models.ShoppingList.objects.get(id = int(list_id))
                
                list_editors = models.EditingUser.objects.filter(shoppingList=list_to_add_to)
                print("add_product - list to add to name: ", list_to_add_to.name, " editors count: ", len(list_editors))
                user_has_right_to_add_product = False
                for editron in list_editors:
                    if editron.normalUser.login == matching_user.login and editron.inviteAccepted == True:
                        user_has_right_to_add_product = True
                        break
                if user_has_right_to_add_product:
                    print("add_product - user has edit right - try to add product")
                    new_product = models.Product(description = product_description, added_to_cart = False, product_list = list_to_add_to)
                    new_product.save()
                    return HttpResponseRedirect( reverse("list_page", kwargs={ "user_profile_url_txt" : get_user_profile_url(matching_user), "list_id": list_to_add_to.id }) )
    return HttpResponseRedirect(reverse("main-page"))


def delete_list(httprequest, user_profile_url_txt, list_id):
    if httprequest.method == "POST":
            if user_is_logged_in(httprequest):
                matching_user = get_logged_in_user_from_request_obj(httprequest)
                if matching_user is not None:
                    print("delete_list aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                    print("delete_list: list to delete id: ",httprequest.POST["list_id"])
                    list_to_delete = models.ShoppingList.objects.get(id = int( httprequest.POST[ "list_id"]))
                    if list_to_delete.owner.login == matching_user.login:
                        list_to_delete.delete()
                        return HttpResponseRedirect( reverse("user_profile_page", kwargs={ "user_profile_url_txt" : get_user_profile_url(matching_user) }) )
    return HttpResponseRedirect("main-page")

def remove_product(httprequest, user_profile_url_txt, list_id):
    if httprequest.method == "POST":
        print("add_product - 1st if - method is POST")
        if user_is_logged_in(httprequest):
            matching_user = get_logged_in_user_from_request_obj(httprequest)
            if matching_user is not None:
                product_to_delete_id = int(httprequest.POST["item_id"])
                product_to_delete = models.Product.objects.get(id=product_to_delete_id)
                list_to_remove_from = product_to_delete.product_list
                list_editors = models.EditingUser.objects.filter(shoppingList = list_to_remove_from)
                user_has_editing_right = False
                for edit_right in list_editors:
                    if edit_right.normalUser.login == matching_user.login:
                        user_has_editing_right = True
                        break
                if user_has_editing_right:
                    product_to_delete.delete()
                    return HttpResponseRedirect( reverse("list_page", kwargs={ "user_profile_url_txt" : get_user_profile_url(matching_user), "list_id": list_to_remove_from.id }) )
    return HttpResponseRedirect(reverse("main-page"))


def change_added_to_cart(httprequest, user_profile_url_txt, list_id):
    if httprequest.method == "POST":
        print("add_product - 1st if - method is POST")
        if user_is_logged_in(httprequest):
            matching_user = get_logged_in_user_from_request_obj(httprequest)
            if matching_user is not None:
                product_to_update_id = int(httprequest.POST["item_id"])
                product_to_update = models.Product.objects.get(id=product_to_update_id)
                list_to_update = product_to_update.product_list
                list_editors = models.EditingUser.objects.filter(shoppingList = list_to_update)
                user_has_editing_right = False
                for edit_right in list_editors:
                    if edit_right.normalUser.login == matching_user.login:
                        user_has_editing_right = True
                        break
                if user_has_editing_right:
                    product_to_update.added_to_cart = not product_to_update.added_to_cart
                    product_to_update.save()
                    return HttpResponseRedirect( reverse("list_page", kwargs={ "user_profile_url_txt" : get_user_profile_url(matching_user), "list_id": list_to_update.id }) )
    return HttpResponseRedirect(reverse("main-page"))


def get_user_matching_to_login(user_login):
    #list_of_users_with_matching_login = models.NormalUser.objects.filter(login = user_login)
    list_of_users_with_matching_login = User.objects.filter(username=user_login)
    if len(list_of_users_with_matching_login) > 0:
        return UserUnified(list_of_users_with_matching_login[0], UserInitType.AUTH_USER)
        # return list_of_users_with_matching_login[0].normaluser
    return None


def prepare_user_login(login_passed_from_user):
    login_passed_from_user = str(login_passed_from_user)
    login_passed_from_user = login_passed_from_user.strip()
    login_passed_from_user = login_passed_from_user.lower()
    return slugify(login_passed_from_user)

def my_validate_password(password):
    pswd_val = True
    try:
        pswd_val = validate_password(password)
    except Exception as exc:
        pswd_val = False
        pass

    print("my_validate_password pswd_val: ", pswd_val)
    return ( pswd_val is None )

def user_is_logged_in(httprequest):
    return httprequest.user.is_authenticated and "user_login" in httprequest.session and httprequest.user.username == httprequest.session["user_login"]

def get_logged_in_user_from_request_obj(httprequest):
    user = httprequest.user
    return UserUnified(user, UserInitType.AUTH_USER)

def generate_user_hash(user_nick):
    random_seed = randint(0, 2147483640)
    user_nick = user_nick + str(random_seed)
    md5_hashed_user_nick = hashlib.md5(user_nick.encode()).hexdigest()[:10]
    users_with_same_hash = models.NormalUser.objects.filter(invitehash = md5_hashed_user_nick)
    if len(users_with_same_hash) > 0:
        i = 0
        hash_with_appendix=""
        while len(users_with_same_hash):
            hash_with_appendix = md5_hashed_user_nick + str(i)
            users_with_same_hash = models.NormalUser.objects.filter(invitehash = md5_hashed_user_nick)
            i = i+1
        md5_hashed_user_nick = hash_with_appendix
    return md5_hashed_user_nick


def hash_password(password, iterations=390000, salt =""):
    hasher = PBKDF2PasswordHasher()
    if salt=="":
        salt = uuid.uuid4().hex
    return hasher.encode(password, salt, iterations )
    
def register_user(httprequest):
    print("register_user - method: ", httprequest.method)
    if httprequest.method == "POST":
        new_user_login = httprequest.POST["user_login"]
        new_user_email = httprequest.POST["user_email"]
        new_user_password_1 = httprequest.POST["user_password_1"].strip()
        new_user_password_2 = httprequest.POST["user_password_2"].strip()
        new_user_nick = httprequest.POST["user_nick"].strip()
        new_user_login = prepare_user_login(new_user_login)

        #matching_existing_login_list = models.NormalUser.objects.filter(login = new_user_login)
        matching_existing_login_list = User.objects.filter(username=new_user_login)
        if len(matching_existing_login_list) > 0 or len(new_user_login) == 0:
            #httprequest.GET["error_flag"] = True
            #httprequest.GET["error_msg"] = "Podaj inny i nie pusty login"
            #return render(httprequest, reverse("main-page"), {"error_flag" : True, "error_msg" : "Podaj inny i nie pusty login"})
            #return HttpResponseRedirect(reverse("main-page"), kwargs={"error_flag" : True, "error_msg" : "Podaj inny i nie pusty login"})
            return render(httprequest, "shopping_list/index.html", context= {"error_flag" : True, "error_msg" : "Podaj inny i nie pusty login"})

        if not my_validate_password(new_user_password_1):
            #return render(httprequest, reverse("main-page"), {"error_flag" : True, "error_msg" : "Hasło nie jest wystarczająco silne"})
            #return HttpResponseRedirect(reverse("main-page"), kwargs={"error_flag" : True, "error_msg" : "Hasło nie jest wystarczająco silne"})
            #httprequest.GET["error_flag"] = True
            #httprequest.GET["error_msg"] = "Hasło nie jest wystarczająco silne"
            return render(httprequest, "shopping_list/index.html", context= {"error_flag" : True, "error_msg" : "Hasło nie jest wystarczająco silne"})
        if new_user_password_1 != new_user_password_2:
            #return render(httprequest, reverse("main-page"), {"error_flag" : True, "error_msg" : "Podane hasła się różnią"})
            #return HttpResponseRedirect(reverse("main-page"), kwargs={"error_flag" : True, "error_msg" : "Podane hasła się różnią"})
            #httprequest.GET["error_flag"] = True
            #httprequest.GET["error_msg"] = "Podane hasła się różnią"
            return render(httprequest, "shopping_list/index.html", context= {"error_flag" : True, "error_msg" : "Podane hasła się różnią"})
        if len(new_user_email) == 0:
            return render(httprequest, "shopping_list/index.html", context= {"error_flag" : True, "error_msg" : "Podaj email"})

        if len(new_user_nick) == 0:
            #return render(httprequest, reverse("main-page"), {"error_flag" : True, "error_msg" : "Podaj nick"})
            #return HttpResponseRedirect(reverse("main-page"), kwargs={"error_flag" : True, "error_msg" : "Podaj nick"})
            #httprequest.GET["error_flag"] = True
            #httprequest.GET["error_msg"] = "Podaj nick"
            return render(httprequest, "shopping_list/index.html", context= {"error_flag" : True, "error_msg" : "Podaj nick"})
        #password_hashed = hashText(new_user_password_1)
        user_hash = generate_user_hash(new_user_nick)
        #new_user = models.NormalUser(nick=new_user_nick, login=new_user_login, password=password_hashed, invitehash=user_hash)
        password_hashed = hash_password(new_user_password_1)
        with transaction.atomic():
            new_user = User(username = new_user_login, password= password_hashed, email = new_user_email, is_staff=False)
            new_user.save()
            new_user_profile = models.NormalUser(user = new_user, nick = new_user_nick, invitehash = user_hash)
            new_user_profile.save()
        return login_user(httprequest)
    return HttpResponseRedirect( reverse("main-page"))


def get_user_profile_url(user):
    return user.login


def do_login_work(httprequest, template_location):
    render_result = None
    if httprequest.method == "POST":
        print("login_user view - enter 1st if")
        user_login = prepare_user_login( httprequest.POST["user_login"] )
        user_password = httprequest.POST["user_password_1"].strip()
        #list_of_users_with_matching_login = models.NormalUser.objects.filter(login = user_login)
        list_of_users_with_matching_login = User.objects.filter(username = user_login)
        print("do login work: list of users with matching login", str(len(list_of_users_with_matching_login)))
        if len(list_of_users_with_matching_login) == 0:
            render_result = render(httprequest, template_location, {"error_flag" : True, "error_msg" : "Niepoprawny login lub hasło"})
            return None, render_result
        matching_user_password = list_of_users_with_matching_login[0].password
        print("login_user: ", matching_user_password, ", type: ", str(type(matching_user_password)))
        # password_matching_to_hash = matchHashedText(matching_user_password, user_password)
        password_matching_to_hash = check_password(user_password, matching_user_password)
        if not password_matching_to_hash:
            render_result =  render(httprequest, template_location, {"error_flag" : True, "error_msg" : "Niepoprawny login lub hasło"})
            return None, render_result
        print("login_user - passed check_password function - before authenticate function")
        user = authenticate(httprequest, username = user_login, password = user_password)
        if user:
            print("login user - pass authenticate function")
            login(httprequest, user)
            user = UserUnified(user, UserInitType.AUTH_USER)
            httprequest.session["user_login"] = user.login
            # user_url = get_user_profile_url(list_of_users_with_matching_login[0])
            return user, None
    return None, render_result


def login_user(httprequest):
    print("login_user - method: ", httprequest.method)
    user, render_result = do_login_work(httprequest, "shopping_list/index.html")
    if not user is None:
        user_url = get_user_profile_url(user)
        return HttpResponseRedirect( reverse("user_profile_page", args=(user_url,)))
    elif not render_result is None:
        return render_result
    else:
        return HttpResponseRedirect("main-page")
    
    '''
    if httprequest.method == "POST":
        print("login_user view - enter 1st if")
        user_login = prepare_user_login( httprequest.POST["user_login"] )
        user_password = httprequest.POST["user_password_1"].strip()
        #list_of_users_with_matching_login = models.NormalUser.objects.filter(login = user_login)
        list_of_users_with_matching_login = User.objects.filter(username = user_login)
        if len(list_of_users_with_matching_login) == 0:
            return render(httprequest, "shopping_list/index.html", {"error_flag" : True, "error_msg" : "Niepoprawny login lub hasło"})
        matching_user_password = list_of_users_with_matching_login[0].password
        print("login_user: ", matching_user_password, ", type: ", str(type(matching_user_password)))
        # password_matching_to_hash = matchHashedText(matching_user_password, user_password)
        password_matching_to_hash = check_password(user_password, matching_user_password)
        if not password_matching_to_hash:
            return render(httprequest, "shopping_list/index.html", {"error_flag" : True, "error_msg" : "Niepoprawny login lub hasło"})
        print("login_user - passed check_password function - before authenticate function")
        user = authenticate(httprequest, username = user_login, password = user_password)
        if user:
            print("login user - pass authenticate function")
            login(httprequest, user)
            user = UserUnified(user, UserInitType.AUTH_USER)
            httprequest.session["user_login"] = user.login
            # user_url = get_user_profile_url(list_of_users_with_matching_login[0])
            user_url = get_user_profile_url(user)
            print("login_user view before green path redirect")
            return HttpResponseRedirect( reverse("user_profile_page", args=(user_url,)))
    return HttpResponseRedirect( reverse("main-page"))
    '''


def login_email_confirm(httprequest, user_profile_url_txt, change_email_url):
    print("login_email_confirm - begin method")
    user, render_result = do_login_work(httprequest, "shopping_list/login_email_change.html")
    if not user is None:
        return HttpResponseRedirect( reverse("update_email_confirm", kwargs= {"user_profile_url_txt" :user_profile_url_txt, "change_email_url": change_email_url} ))
    elif not render_result is None:
        return render_result
    else:
        return HttpResponseRedirect("main-page")

def login_view(httprequest):
    return True

'''
def register_view(httprequest):
    if httprequest.method=="POST":
        new_login = httprequest.POST["register_login_input"]
        new_password_1= httprequest.POST["register_password_1"]
        new_password_2 = httprequest.POST["register_password_2"]
        print(new_login,", ", new_password_1, ", ", new_password_2)
        new_login_pcesd= slugify(new_login.lower())
        users_with_same_login = models.User.objects.filter(login=new_login_pcesd)
        if new_login_pcesd == "" or len(users_with_same_login) > 0:
            httprequest.GET["has_error"] = True
            httprequest.GET["error_description"] = "Wybierz inny login"
            return HttpResponseRedirect( reverse("main-page"))
        if new_password_1 == "" or new_password_1 != new_password_2:
            httprequest.GET["error_description"] = "Hasła się różnią"
            httprequest.GET["has_error"] = True
            return HttpResponseRedirect( reverse("main-page"))
        user = models.User(login = new_login_pcesd, password = new_password_1)
        user.save()
        httprequest.session["user_login"] = user.login
        httprequest.GET["has_error"] = False
        httprequest.GET["error_description"] = ""
        httprequest.GET["marker"] = str(user.login)+"_aaaaaaaaa"
        return HttpResponseRedirect( reverse("list-page", args = [user.login]) )
    return HttpResponseRedirect( reverse("main-page"))


def list_view(httprequest, loginslug):
    if not ('user_login' in httprequest.session):
        print("No session key in request")
        return HttpResponseRedirect( reverse("main-page") )
    print("Session key present in request")
    return render(httprequest, "shopping_list/products_list.html")


class IndexView(View):
    def post(self, request):
        if 'session_key' in request.session:
            try:
                user_login = request.POST["user_login"]
            except:
                return HttpResponseNotFound("No such user")
            return HttpResponseRedirect( reverse("list-page", args = [user_login]) )
        return render(request, "shopping_list/index.html")
    def get(self, request):
        if 'session_key' in request.session:
            try:
                user_login = request.GET["user_login"]
            except:
                return HttpResponseNotFound("No such user")
            return HttpResponseRedirect( reverse("list-page", args = [user_login]) )
        return render(request, "shopping_list/index.html")

'''




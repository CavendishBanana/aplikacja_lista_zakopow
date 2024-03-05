from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import View
from django.utils.text import slugify
from django.db.models import Q
from . import models
from random import randint
import hashlib
import uuid 


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

def index(httprequest):
    if "user_login" in httprequest.session:
        user_login = httprequest.session["user_login"]
        user_list = models.NormalUser.objects.filter(login = user_login)
        if len(user_list) > 0:
            user = user_list[0]
            user_url = get_user_profile_url(user)
            return HttpResponseRedirect( reverse("user_profile_page", args=(user_url,)))
        httprequest.session.pop("user_login")
        httprequest.session.modified=True
    return render(httprequest, "shopping_list/index.html")


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
    if "user_login" in httprequest.session:
        print("load_user_profile view - passed check if user_login in request.session")
        user_login = httprequest.session["user_login"]
        user_list = models.NormalUser.objects.filter(login = user_login)
        if len(user_list) > 0:
            print("load_user_profile view - passed check if user with user_login exists")
            user = user_list[0]
            lists_owned = models.ShoppingList.objects.filter(owner=user)
            lists_being_edited = models.ShoppingList.objects.filter(~Q(owner=user) & Q(editor=user))
            resp_list_owned = []
            for lst in lists_owned:
                resp_list_owned.append( { "name" : lst.name, "create_date": lst.create_date, "id" : lst.id, "list_link" : reverse("list_page", args=[get_user_profile_url(user), lst.id]) })
            resp_list_edited = []
            for lst in lists_being_edited:
                resp_list_edited.append( { "name" : lst.name, "create_date": lst.create_date, "id": lst.id, "list_link" : reverse("list_page", args=[get_user_profile_url(user), lst.id]) } )
            invites = models.EditingUser.objects.filter(normalUser = user, inviteAccepted = False)
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


def logout_user(httprequest, user_profile_url_txt):
    print("miau miau miau miau")
    if httprequest.method == "POST":
        print("hrum hrum")
        if "user_login" in httprequest.session:
            print("logout_user - pass user_login in session")
            user_login = httprequest.session["user_login"]
            user_list = models.NormalUser.objects.filter(login = user_login)
            if len(user_list) > 0:
                print("kukuryku")
                del httprequest.session
    return HttpResponseRedirect( reverse("main-page"))


def create_new_list(httprequest, user_profile_url_txt):
    if httprequest.method == "POST":
        if "user_login" in httprequest.session:
            matching_user=get_user_matching_to_login(httprequest.session["user_login"])
            if matching_user is not None:
                new_list_name = httprequest.POST["new_list_name"]
                new_list = models.ShoppingList(name=new_list_name, owner=matching_user)
                new_list.save()
                editionRight = models.EditingUser(normalUser = matching_user, shoppingList = new_list)
                editionRight.save() 
                list_id = new_list.id
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
        if "user_login" in httprequest.session:
            user_login = httprequest.session["user_login"]
            matching_user = get_user_matching_to_login(user_login)
            if matching_user is not None:  
                list_id = int(list_id)
                shopping_list_list = models.ShoppingList.objects.filter(id=list_id)
                shopping_list = shopping_list_list[0]
                list_owner = shopping_list.owner
                list_editors = models.EditingUser.objects.filter(shoppingList=shopping_list).filter(~Q(normalUser=list_owner))
                user_is_authorized_to_edit = False
                #i = 0
                for editor_tmp in list_editors:
                    editor = editor_tmp.normalUser
                    if user_login == editor.login and editor_tmp.inviteAccepted == True:
                
                        user_is_authorized_to_edit = True
                        break
                    #i=i+1
                #del list_editors[i]
                user_is_owner = (user_login == list_owner.login)
                user_is_authorized_to_edit = ( user_is_authorized_to_edit or user_is_owner )

                if user_is_authorized_to_edit:
                    shoping_list_items_0 = shopping_list.listproducts.all()
                    shopping_list_items = []
                    for item in shoping_list_items_0:
                        shopping_list_items.append( { "id" : item.id, "item_description" : item.description, "in_cart" : (item.added_to_cart == True) } )
                
                    return render(httprequest, "shopping_list/products_list.html", { "products" : shopping_list_items, "is_owner": user_is_owner, "list_name": shopping_list.name, \
                                                                                    "create_date" : shopping_list.create_date, "owner_nick" :  list_owner.nick, \
                                                                                        "add_new_url" : reverse( "add_product", kwargs={ "user_profile_url_txt": get_user_profile_url(matching_user), "list_id": list_id  } ),\
                                                                                        "list_id":list_id, "user_profile_url_txt" : get_user_profile_url(matching_user) ,"editors" : list_editors, "error_data" : error_data })
                user_url = get_user_profile_url(matching_user)
                return HttpResponseRedirect( reverse("user_profile_page", args=(user_url,))) 
    return HttpResponseRedirect( reverse("main-page"))


def remove_editor(httprequest, user_profile_url_txt, list_id):
    if httprequest.method == "POST":
        print("remove_editor - 1st if - method is POST")
        if "user_login" in httprequest.session:
            matching_user = get_user_matching_to_login(httprequest.session["user_login"])
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
        if "user_login" in httprequest.session:
            matching_user = get_user_matching_to_login(httprequest.session["user_login"])
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
        if "user_login" in httprequest.session:
            matching_user = get_user_matching_to_login(httprequest.session["user_login"])
            if matching_user is not None:
                list_invited_to = models.ShoppingList.objects.get(id = int( httprequest.POST["list_id"] ))
                edition_right = models.EditingUser.objects.get(normalUser = matching_user, shoppingList = list_invited_to)
                edition_right.inviteAccepted = True
                edition_right.save()
                return HttpResponseRedirect( reverse("user_profile_page", kwargs={ "user_profile_url_txt" : get_user_profile_url(matching_user)}))
    HttpResponseRedirect(reverse("main-page"))

def add_product(httprequest, user_profile_url_txt, list_id):
    if httprequest.method == "POST":
        print("add_product - 1st if - method is POST")
        if "user_login" in httprequest.session:
            matching_user = get_user_matching_to_login(httprequest.session["user_login"])
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
            if "user_login" in httprequest.session:
                matching_user = get_user_matching_to_login(httprequest.session["user_login"])
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
        if "user_login" in httprequest.session:
            matching_user = get_user_matching_to_login(httprequest.session["user_login"])
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
        if "user_login" in httprequest.session:
            matching_user = get_user_matching_to_login(httprequest.session["user_login"])
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
    list_of_users_with_matching_login = models.NormalUser.objects.filter(login = user_login)
    if len(list_of_users_with_matching_login) > 0:
        return list_of_users_with_matching_login[0]
    return None


def prepare_user_login(login_passed_from_user):
    login_passed_from_user = str(login_passed_from_user)
    login_passed_from_user = login_passed_from_user.strip()
    login_passed_from_user = login_passed_from_user.lower()
    return slugify(login_passed_from_user)

def validate_password(password):
    return True

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


def register_user(httprequest):
    print("register_user - method: ", httprequest.method)
    if httprequest.method == "POST":
        new_user_login = httprequest.POST["user_login"]
        new_user_password_1 = httprequest.POST["user_password_1"]
        new_user_password_2 = httprequest.POST["user_password_2"]
        new_user_nick = httprequest.POST["user_nick"]
        new_user_login = prepare_user_login(new_user_login)

        matching_existing_login_list = models.NormalUser.objects.filter(login = new_user_login)
        if len(matching_existing_login_list) > 0 or len(new_user_login) == 0:
            #httprequest.GET["error_flag"] = True
            #httprequest.GET["error_msg"] = "Podaj inny i nie pusty login"
            #return render(httprequest, reverse("main-page"), {"error_flag" : True, "error_msg" : "Podaj inny i nie pusty login"})
            #return HttpResponseRedirect(reverse("main-page"), kwargs={"error_flag" : True, "error_msg" : "Podaj inny i nie pusty login"})
            return render(httprequest, "shopping_list/index.html", context= {"error_flag" : True, "error_msg" : "Podaj inny i nie pusty login"})

        if not validate_password(new_user_password_1):
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
        if len(new_user_nick) == 0:
            #return render(httprequest, reverse("main-page"), {"error_flag" : True, "error_msg" : "Podaj nick"})
            #return HttpResponseRedirect(reverse("main-page"), kwargs={"error_flag" : True, "error_msg" : "Podaj nick"})
            #httprequest.GET["error_flag"] = True
            #httprequest.GET["error_msg"] = "Podaj nick"
            return render(httprequest, "shopping_list/index.html", context= {"error_flag" : True, "error_msg" : "Podaj nick"})
        password_hashed = hashText(new_user_password_1)
        user_hash = generate_user_hash(new_user_nick)
        new_user = models.NormalUser(nick=new_user_nick, login=new_user_login, password=password_hashed, invitehash=user_hash)
        new_user.save()
        return login_user(httprequest)
    return HttpResponseRedirect( reverse("main-page"))


def get_user_profile_url(user):
    return user.login


def login_user(httprequest):
    print("login_user - method: ", httprequest.method)
    if httprequest.method == "POST":
        print("login_user view - enter 1st if")
        user_login = prepare_user_login( httprequest.POST["user_login"] )
        user_password = httprequest.POST["user_password_1"]
        list_of_users_with_matching_login = models.NormalUser.objects.filter(login = user_login)
        if len(list_of_users_with_matching_login) == 0:
            return render(httprequest, "shopping_list/index.html", {"error_flag" : True, "error_msg" : "Niepoprawny login lub hasło"})
        matching_user_password = list_of_users_with_matching_login[0].password
        password_matching_to_hash = matchHashedText(matching_user_password, user_password)
        if not password_matching_to_hash:
            return render(httprequest, "shopping_list/index.html", {"error_flag" : True, "error_msg" : "Niepoprawny login lub hasło"})
        httprequest.session["user_login"] = list_of_users_with_matching_login[0].login
        user_url = get_user_profile_url(list_of_users_with_matching_login[0])
        print("login_user view before green path redirect")
        return HttpResponseRedirect( reverse("user_profile_page", args=(user_url,)))
    return HttpResponseRedirect( reverse("main-page"))


# return render(httprequest, "shopping_list/html_template.html", {"month_name" : month, "month_list" : "list for: "+months[chosen_month_no]})


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




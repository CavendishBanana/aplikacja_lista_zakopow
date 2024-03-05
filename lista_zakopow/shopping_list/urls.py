from django.urls import path
from . import views
#from django_distill import distill_path

urlpatterns = [
    path("", views.index, name="main-page"),
    path("login/", views.login_user, name = "login_user"),
    path("register/", views.register_user, name = "register_user"),
    path("user-profile/<slug:user_profile_url_txt>/", views.load_user_profile, name = "user_profile_page"),
    path("user-profile/<slug:user_profile_url_txt>/create_new_list/", views.create_new_list, name= "create_new_list"),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>", views.list_view, name = "list_page"),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/additem", views.add_product, name="add_product"),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/removeitem"  ,views.remove_product ,name="remove_item_from_list" ),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/changeadded" , views.change_added_to_cart ,name="change_added_to_cart" ),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/removelist" , views.delete_list ,name="delete_list" ),
    path ("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/removeeditor", views.remove_editor, name="remove_user_from_list_editors"),
    path ("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/inviteeditor", views.invite_editor,name="invite_to_list_using_hash"),
    path ("user-profile/<slug:user_profile_url_txt>/acceptinvite", views.accept_invite,name="accept_invite"),
    path ("user-profile/<slug:user_profile_url_txt>/logoutuser", views.logout_user,name="logoutuser")

    
    
    #path("changebought/", views.change_bought_flag, name = "change_bought_flag"),
    #path("delete/", views.delete_product, name="delete_product"),
    #path("addnew/", views.add_new_product, name="add_new_product")
    
]
'''
urlpatterns = [
    distill_path('', views.index, name="main-page", distill_file = "index.html"),
    distill_path('changebought', views.change_bought_flag, name="change_bought_flag", distill_file = "index_ch.html"),
    distill_path('delete', views.delete_product, name="delete_product", distill_file = "index.html"),
    distill_path('addnew', views.add_new_product, name="add_new_product", distill_file = "index.html")
]
'''
'''
urlpatterns = [
    distill_path('', views.index, name="main-page", distill_file = "index.html"),
    distill_path('changebought', views.change_bought_flag, name="change_bought_flag", distill_file = "index.html"),
    distill_path('delete', views.delete_product, name="delete_product", distill_file = "index.html"),
    distill_path('addnew', views.add_new_product, name="add_new_product", distill_file = "index.html")
]
'''
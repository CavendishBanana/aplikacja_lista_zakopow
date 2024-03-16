from django.urls import path
from . import views
#from django_distill import distill_path

urlpatterns = [
    path("", views.index, name="main-page"),
    path("cookiespolicy", views.cookies_policy_view, name="cookies_policy"),
    path("login/", views.login_user, name = "login_user"),
    path("register/", views.register_user, name = "register_user"),
    path("user-profile/<slug:user_profile_url_txt>/", views.load_user_profile, name = "user_profile_page"),
    path("user-profile/<slug:user_profile_url_txt>/create_new_list/", views.create_new_list, name= "create_new_list"),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>", views.list_view, name = "list_page"),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/getproducts", views.get_products_view, name = "get_products"),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/additem", views.add_product, name="add_product"),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/removeitem"  ,views.remove_product ,name="remove_item_from_list" ),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/changeadded" , views.change_added_to_cart ,name="change_added_to_cart" ),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/removelist" , views.delete_list ,name="delete_list" ),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/removeeditor", views.remove_editor, name="remove_user_from_list_editors"),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/inviteeditor", views.invite_editor,name="invite_to_list_using_hash"),
    path("user-profile/<slug:user_profile_url_txt>/acceptinvite", views.accept_invite,name="accept_invite"),
    path("user-profile/<slug:user_profile_url_txt>/logoutuser", views.logout_user,name="logoutuser"),
    path("user-profile/<slug:user_profile_url_txt>/editprofile", views.edit_profile,name="edit_profile"),
    path("user-profile/<slug:user_profile_url_txt>/editprofile/updatenick", views.update_nick, name="update_nick"),
    path("user-profile/<slug:user_profile_url_txt>/editprofile/updatepassword", views.update_password, name="update_password"),
    path("user-profile/<slug:user_profile_url_txt>/editprofile/updateemail", views.update_email, name="update_email"),
    path("user-profile/<slug:user_profile_url_txt>/editprofile/updateemailconfirm/<str:change_email_url>", views.update_email_confirm, name="update_email_confirm"),
    path("user-profile/<slug:user_profile_url_txt>/editprofile/loginemailconfirm/<str:change_email_url>", views.login_email_confirm, name="login_email_confirm"),
    path("user-profile/<slug:user_profile_url_txt>/editprofile/deleteaccount", views.delete_account, name="delete_account"),
    path("user-profile/<slug:user_profile_url_txt>/rejectinvite/", views.reject_invite, name= "reject_invite"),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/leavelist" , views.leave_list_of_other_user , name="leave_list" ),
    path("user-profile/<slug:user_profile_url_txt>/list/<int:list_id>/cancelinvite" , views.cancel_invite_to_other_user , name="cancel_invite" )
    
]

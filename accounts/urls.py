from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", 
        views.register, 
        name="register"),
    path(
        "login/", 
        LoginView.as_view(template_name="accounts/login.html",), 
        name="login"),
    path(
            "logout/",
            LogoutView.as_view(),
            name="logout",
        ),
    path(
            "profile/",
            views.profile,
            name="profile"
        ),
    path(
            "profile/edit/",
            views.profile_edit,
            name="profile_edit",
        ),
    path(
            "users/",
            views.UserListView.as_view(),
            name="user_list",
        ),
    path(
            "users/<str:username>/",
            views.UserPublicProfileView.as_view(),
            name="public_profile",
        ),

]
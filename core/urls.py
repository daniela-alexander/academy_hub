from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),

    path(
        "contact/",
        views.ContactMessageCreateView.as_view(),
        name="contact",
    ),
    path(
        "contact/messages/",
        views.ContactMessageListView.as_view(),
        name="contact_message_list",
    ),
    path(
        "contact/messages/<int:pk>/",
        views.ContactMessageDetailView.as_view(),
        name="contact_message_detail",
    ),
    path(
        "contact/messages/<int:pk>/edit/",
        views.ContactMessageUpdateView.as_view(),
        name="contact_message_update",
    ),
    path(
        "contact/messages/<int:pk>/delete/",
        views.ContactMessageDeleteView.as_view(),
        name="contact_message_delete",
    ),
]

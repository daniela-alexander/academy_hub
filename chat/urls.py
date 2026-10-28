from django.urls import path

from . import views_web

app_name = "chat"

urlpatterns = [
    path("", views_web.ConversationListView.as_view(), name="list"),
    path("<int:pk>/", views_web.ConversationDetailView.as_view(), name="detail"),
    path("create/group/", views_web.CreateGroupView.as_view(), name="create_group"),
    path(
        "create/direct/",
        views_web.CreateDirectConversationView.as_view(),
        name="create_direct",
    ),
]

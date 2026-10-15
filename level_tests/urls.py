from django.urls import path

from . import views

app_name = "level_tests"

urlpatterns = [
    path("", views.LevelTestListView.as_view(), name="list"),
    path("create/", views.LevelTestCreateView.as_view(), name="create"),
    path("<int:pk>/", views.LevelTestDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.LevelTestUpdateView.as_view(), name="update"),
    path("<int:pk>/attempt/", views.LevelTestAttemptView.as_view(), name="attempt"),
]

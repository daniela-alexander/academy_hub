from django.urls import path

from . import views

app_name = "evaluations"

urlpatterns = [
    path("", views.EvaluationListView.as_view(), name="list"),
    path(
        "enrollment/<int:enrollment_pk>/create/",
        views.EvaluationCreateView.as_view(),
        name="create",
    ),
    path("<int:pk>/edit/", views.EvaluationUpdateView.as_view(), name="update"),
]

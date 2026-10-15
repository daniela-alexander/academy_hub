from django.urls import path

from . import views

app_name = "talent"

urlpatterns = [
    path("", views.MyPassportView.as_view(), name="passport"),
    path("edit/", views.MyPassportEditView.as_view(), name="passport_edit"),

    path("competences/", views.CompetenceListView.as_view(), name="competence_list"),
    path("competences/create/", views.CompetenceCreateView.as_view(), name="competence_create"),
    path("competences/<int:pk>/edit/", views.CompetenceUpdateView.as_view(), name="competence_update"),

    path(
        "student/<int:student_pk>/add-entry/",
        views.PassportEntryCreateView.as_view(),
        name="entry_create",
    ),
]

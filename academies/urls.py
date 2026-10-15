from django.urls import path

from . import views

app_name = "academies"

urlpatterns = [
        path("", views.AcademyListView.as_view(), name="list"),
        path("create/", views.AcademyCreateView.as_view(), name="create"),
        path("favorites/", views.AcademyFavoriteListView.as_view(), name="favorites"),
        path("<slug:slug>/", views.AcademyDetailView.as_view(), name="detail"),
        path("<slug:slug>/edit/", views.AcademyUpdateView.as_view(), name="update"),
        path("<slug:slug>/delete/", views.AcademyDeleteView.as_view(), name="delete"),
        path("<slug:slug>/favorite/", views.toggle_academy_favorite, name="toggle_favorite"),

        path("teachers/", views.TeacherListView.as_view(), name="teacher_list"),
        path(
                "teachers/create/<int:academy_pk>/",
                views.TeacherCreateView.as_view(),
                name="teacher_create",
        ),
        path("teachers/<int:pk>/", views.TeacherDetailView.as_view(), name="teacher_detail"),
        path("teachers/<int:pk>/edit/", views.TeacherUpdateView.as_view(), name="teacher_update"),
        path("teachers/<int:pk>/delete/", views.TeacherDeleteView.as_view(), name="teacher_delete"),
]
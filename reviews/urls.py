from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("mine/", views.MyReviewListView.as_view(), name="mine"),

    path(
        "course/<int:course_pk>/create/",
        views.CourseReviewCreateView.as_view(),
        name="course_create",
    ),
    path(
        "course/<int:pk>/edit/",
        views.CourseReviewUpdateView.as_view(),
        name="course_update",
    ),
    path(
        "course/<int:pk>/delete/",
        views.CourseReviewDeleteView.as_view(),
        name="course_delete",
    ),

    path(
        "academy/<slug:slug>/create/",
        views.AcademyReviewCreateView.as_view(),
        name="academy_create",
    ),
    path(
        "academy/<int:pk>/edit/",
        views.AcademyReviewUpdateView.as_view(),
        name="academy_update",
    ),
    path(
        "academy/<int:pk>/delete/",
        views.AcademyReviewDeleteView.as_view(),
        name="academy_delete",
    ),
    path(
        "course-reviews/",
        views.CourseReviewListView.as_view(),
        name="course_review_list",
),
]

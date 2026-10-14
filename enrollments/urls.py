from django.urls import path

from . import views

app_name = "enrollments"

urlpatterns = [
    path("", views.EnrollmentListView.as_view(), name="list"),
    path(
        "create/<int:convocatoria_pk>/",
        views.EnrollmentCreateView.as_view(),
        name="create",
    ),
    path(
        "<int:pk>/",
        views.EnrollmentDetailView.as_view(),
        name="detail",
    ),
    path(
        "<int:pk>/cancel/",
        views.EnrollmentCancelView.as_view(),
        name="cancel",
    ),
    path(
        "<int:pk>/approve/",
        views.EnrollmentApproveView.as_view(),
        name="approve",
    ),
    path(
        "<int:pk>/reject/",
        views.EnrollmentRejectView.as_view(),
        name="reject",
    ),
    path(
        "<int:pk>/enroll/",
        views.EnrollmentEnrollView.as_view(),
        name="enroll",
    ),
    path(
        "academy/",
        views.AcademyEnrollmentListView.as_view(),
        name="academy_list",
    ),
    path(
        "<int:enrollment_pk>/answers/create/",
        views.EnrollmentAnswerCreateView.as_view(),
        name="answer_create",
    ),
    path(
        "<int:enrollment_pk>/documents/create/",
        views.EnrollmentDocumentCreateView.as_view(),
        name="document_create",
    ),
    path(
        "documents/<int:pk>/verify/",
        views.EnrollmentDocumentVerifyView.as_view(),
        name="document_verify",
    ),
]

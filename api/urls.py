from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.accounts import UserViewSet
from api.views.academies import AcademyViewSet, TeacherViewSet
from api.views.auth import (
    ChangePasswordAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    RegisterAPIView,
)
from api.views.courses import (
    CategoryViewSet,
    CourseFavoriteViewSet,
    CourseViewSet,
)
from api.views.enrollments import (
    ConvocatoriaReserveViewSet,
    EnrollmentViewSet,
)
from api.views.evaluations import EvaluationViewSet
from api.views.level_tests import LevelTestViewSet
from api.views.notifications import NotificationViewSet
from api.views.payments import (
    DiscountViewSet,
    PaymentViewSet,
    ScholarshipViewSet,
)
from api.views.reviews import (
    AcademyReviewViewSet,
    CourseReviewViewSet,
    MyReviewViewSet,
)
from api.views.stats import StatsAPIView
from api.views.talent import (
    CompetenceViewSet,
    PassportEntryViewSet,
    TalentPassportViewSet,
)

app_name = "api"

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("academies", AcademyViewSet, basename="academy")
router.register("teachers", TeacherViewSet, basename="teacher")
router.register("courses", CourseViewSet, basename="course")
router.register("categories", CategoryViewSet, basename="category")
router.register("course-favorites", CourseFavoriteViewSet, basename="course-favorite")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("convocatorias", ConvocatoriaReserveViewSet, basename="convocatoria")
router.register("course-reviews", CourseReviewViewSet, basename="course-review")
router.register("academy-reviews", AcademyReviewViewSet, basename="academy-review")
router.register("my-reviews", MyReviewViewSet, basename="my-review")
router.register("discounts", DiscountViewSet, basename="discount")
router.register("payments", PaymentViewSet, basename="payment")
router.register("scholarships", ScholarshipViewSet, basename="scholarship")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("evaluations", EvaluationViewSet, basename="evaluation")
router.register("competences", CompetenceViewSet, basename="competence")
router.register("passport", TalentPassportViewSet, basename="passport")
router.register("passport-entries", PassportEntryViewSet, basename="passport-entry")
router.register("level-tests", LevelTestViewSet, basename="level-test")

urlpatterns = [
    # Autenticación
    path("auth/register/", RegisterAPIView.as_view(), name="auth-register"),
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("auth/me/", MeAPIView.as_view(), name="auth-me"),
    path(
        "auth/change-password/",
        ChangePasswordAPIView.as_view(),
        name="auth-change-password",
    ),

    # Stats
    path("stats/", StatsAPIView.as_view(), name="stats"),
]

urlpatterns += router.urls

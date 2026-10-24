from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from courses.models import Course
from dashboard.cache import get_global_stats
from enrollments.models import Enrollment
from payments.models import Payment
from reviews.models import CourseReview


class DashboardView(LoginRequiredMixin, TemplateView):

    def get_template_names(self):
        user = self.request.user
        if user.is_staff:
            return ["dashboard/staff_dashboard.html"]
        if user.is_academy:
            return ["dashboard/academy_dashboard.html"]
        return ["dashboard/student_dashboard.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # ------------------------------------------------------------
        # 1. Estadísticas globales (CACHEADAS)
        # ------------------------------------------------------------
        stats = get_global_stats()
        context["total_courses"] = stats["total_courses"]
        context["total_enrollments"] = stats["total_enrollments"]
        context["total_reviews"] = stats["total_reviews"]
        context["avg_rating"] = stats["avg_rating"]
        context["total_revenue"] = stats["total_revenue"]

        # ------------------------------------------------------------
        # 2. Datos por usuario (NO cacheados)
        # ------------------------------------------------------------
        if user.is_academy:
            context["my_courses"] = Course.objects.filter(academy__owner=user)
            context["my_enrollments"] = Enrollment.objects.filter(
                convocatoria__course__academy__owner=user
            )

        elif user.is_student:
            context["my_enrollments"] = Enrollment.objects.filter(student=user)
            context["my_payments"] = Payment.objects.filter(enrollment__student=user)
            context["my_reviews"] = CourseReview.objects.filter(student=user)

        return context
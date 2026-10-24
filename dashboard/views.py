from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from courses.models import Course, CourseStatus
from enrollments.models import Enrollment
from payments.models import Payment
from reviews.models import CourseReview

from django.db.models import Count, Avg, Sum



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

        context["total_courses"] = Course.objects.count()
        context["total_enrollments"] = Enrollment.objects.count()
        context["total_reviews"] = CourseReview.objects.count()

        context["avg_rating"] = (
            CourseReview.objects.aggregate(avg=Avg("rating"))["avg"] or 0
        )

        context["total_revenue"] = (
            Payment.objects.filter(status="paid")
            .aggregate(total=Sum("amount"))["total"] or 0
        )

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

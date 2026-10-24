from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Convocatoria, Course
from enrollments.models import Enrollment
from reviews.models import CourseReview

User = get_user_model()


class StatsAPIView(APIView):
    def get(self, request):
        total_courses = Course.objects.count()
        active_courses = Course.objects.filter(status="published").count()
        total_academies = User.objects.filter(is_academy=True).count()
        total_students = User.objects.filter(is_student=True).count()
        total_enrollments = Enrollment.objects.count()
        total_reviews = CourseReview.objects.count()
        avg_rating = CourseReview.objects.aggregate(avg=Avg("rating"))["avg"] or 0
        avg_price = Convocatoria.objects.filter(is_active=True).aggregate(
            avg=Avg("price")
        )["avg"] or 0

        return Response(
            {
                "courses": total_courses,
                "active_courses": active_courses,
                "academies": total_academies,
                "students": total_students,
                "enrollments": total_enrollments,
                "reviews": total_reviews,
                "avg_rating": round(float(avg_rating), 2),
                "avg_price": str(avg_price),
            }
        )

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from academies.models import Academy
from courses.models import Course

from .forms import AcademyReviewForm, CourseReviewForm
from .models import AcademyReview, CourseReview

logger = logging.getLogger(__name__)


class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_student


class CourseReviewCreateView(StudentRequiredMixin, CreateView):
    model = CourseReview
    form_class = CourseReviewForm
    template_name = "reviews/course_review_form.html"

    def get_course(self):
        return get_object_or_404(Course, pk=self.kwargs["course_pk"])

    def form_valid(self, form):
        course = self.get_course()

        existing = CourseReview.objects.filter(
            student=self.request.user,
            course=course,
        ).exists()

        if existing:
            messages.error(
                self.request,
                "Ya has valorado este curso.",
            )
            return redirect(course.get_absolute_url())

        form.instance.student = self.request.user
        form.instance.course = course
        response = super().form_valid(form)
        messages.success(self.request, "Valoración publicada.")
        logger.info(
            "CourseReview created: id=%s student=%s",
            self.object.pk,
            self.request.user.pk,
        )
        return response

    def get_success_url(self):
        return self.object.course.get_absolute_url()

class CourseReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CourseReview
    form_class = CourseReviewForm
    template_name = "reviews/course_review_form.html"

    def test_func(self):
        return self.get_object().student == self.request.user

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class CourseReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CourseReview
    template_name = "reviews/course_review_confirm_delete.html"

    def test_func(self):
        return self.get_object().student == self.request.user

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class AcademyReviewCreateView(StudentRequiredMixin, CreateView):
    model = AcademyReview
    form_class = AcademyReviewForm
    template_name = "reviews/academy_review_form.html"

    def get_academy(self):
        return get_object_or_404(Academy, slug=self.kwargs["slug"])

    def form_valid(self, form):
        academy = self.get_academy()

        existing = AcademyReview.objects.filter(
            student=self.request.user,
            academy=academy,
        ).exists()

        if existing:
            messages.error(
                self.request,
                "Ya has valorado esta academia.",
            )
            return redirect(
                "academies:detail",
                slug=academy.slug,
            )

        form.instance.student = self.request.user
        form.instance.academy = academy
        response = super().form_valid(form)
        messages.success(self.request, "Valoración publicada.")
        return response

    def get_success_url(self):
        return reverse("academies:detail", kwargs={"slug": self.object.academy.slug})

class AcademyReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AcademyReview
    form_class = AcademyReviewForm
    template_name = "reviews/academy_review_form.html"

    def test_func(self):
        return self.get_object().student == self.request.user


class AcademyReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AcademyReview
    template_name = "reviews/academy_review_confirm_delete.html"

    def test_func(self):
        return self.get_object().student == self.request.user


class MyReviewListView(LoginRequiredMixin, ListView):
    template_name = "reviews/my_reviews.html"
    context_object_name = "reviews"

    def get_queryset(self):
        return CourseReview.objects.filter(
            student=self.request.user
        ).select_related("course")

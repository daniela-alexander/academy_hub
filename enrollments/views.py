import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from courses.models import Course
from core.rate_limit import check_rate_limit
from .models import Enrollment, EnrollmentStatus

from courses.models import Convocatoria

from dashboard.cache import invalidate_global_stats

from .forms import (
    EnrollmentAnswerForm,
    EnrollmentDocumentForm,
    EnrollmentForm,
)
from .models import (
    Enrollment,
    EnrollmentAnswer,
    EnrollmentDocument,
    EnrollmentStatus,
    WaitlistEntry,
)

logger = logging.getLogger(__name__)


class EnrollmentListView(LoginRequiredMixin, ListView):
    model = Enrollment
    template_name = "enrollments/my_enrollment_list.html"
    context_object_name = "enrollments"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Enrollment.objects
            .filter(student=self.request.user)
            .select_related("convocatoria", "convocatoria__course")
            .order_by("-created_at")
        )

        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = EnrollmentStatus.choices
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["querystring"] = query_params.urlencode()
        return context


class EnrollmentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Enrollment
    template_name = "enrollments/enrollment_detail.html"
    context_object_name = "enrollment"

    def test_func(self):
        enrollment = self.get_object()
        return (
            enrollment.student == self.request.user
            or enrollment.convocatoria.course.academy.owner == self.request.user
        )


class EnrollmentCreateView(LoginRequiredMixin, CreateView):
    model = Enrollment
    form_class = EnrollmentForm
    template_name = "enrollments/enrollment_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.convocatoria = get_object_or_404(
            Convocatoria,
            pk=kwargs["convocatoria_pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["student"] = self.request.user
        kwargs["convocatoria"] = self.convocatoria
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["convocatoria"] = self.convocatoria
        return context

    def form_valid(self, form):

        rate_key = f"academyhub:rate:enrollments:{self.request.user.pk}"

        if not check_rate_limit(rate_key, limit=5, window=60):
            messages.error(
                self.request,
                "Has realizado demasiadas inscripciones. Inténtalo más tarde.",
            )
            return self.form_invalid(form)
        
        existing = Enrollment.objects.filter(
            student=self.request.user,
            convocatoria=self.convocatoria,
        ).exists()
        
        if existing:
            messages.error(
                self.request,
                "Ya tienes una inscripción en esta convocatoria.",
            )
            return self.form_invalid(form)

        if self.convocatoria.is_full:
            WaitlistEntry.objects.get_or_create(
                student=self.request.user,
                convocatoria=self.convocatoria,
                defaults={
                    "position": WaitlistEntry.objects.filter(
                        convocatoria=self.convocatoria
                    ).count() + 1,
                },
            )
            messages.warning(
                self.request,
                "La convocatoria está llena. Te hemos añadido a la lista de espera.",
            )
            # No creamos Enrollment: redirigimos al listado de inscripciones.
            return redirect("enrollments:list")

        response = super().form_valid(form)
        invalidate_global_stats()
        messages.success(self.request, "Inscripción enviada correctamente.")
        logger.info(
            "Enrollment created: id=%s student=%s",
            self.object.pk,
            self.request.user.pk,
        )
        return response

    def get_success_url(self):
        return reverse("enrollments:detail", kwargs={"pk": self.object.pk})


class EnrollmentCancelView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Enrollment
    fields = []
    template_name = "enrollments/enrollment_confirm_cancel.html"

    def test_func(self):
        enrollment = self.get_object()
        return enrollment.student == self.request.user

    def form_valid(self, form):
        enrollment = form.save(commit=False)
        enrollment.status = EnrollmentStatus.CANCELLED
        enrollment.save()
        messages.success(self.request, "Inscripción cancelada.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("enrollments:list")


class AcademyEnrollmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Enrollment
    template_name = "enrollments/academy_enrollment_list.html"
    context_object_name = "enrollments"
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_academy

    def get_queryset(self):
        queryset = (
            Enrollment.objects
            .filter(convocatoria__course__academy__owner=self.request.user)
            .select_related(
                "student",
                "convocatoria",
                "convocatoria__course",
            )
            .order_by("-created_at")
        )

        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        course_id = self.request.GET.get("course")
        if course_id:
            queryset = queryset.filter(convocatoria__course_id=course_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["statuses"] = EnrollmentStatus.choices
        context["courses"] = Course.objects.filter(
            academy__owner=self.request.user
        ).order_by("title")

        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["querystring"] = query_params.urlencode()

        return context


class EnrollmentApproveView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Enrollment
    fields = []
    template_name = "enrollments/enrollment_confirm_approve.html"

    def test_func(self):
        enrollment = self.get_object()
        return enrollment.convocatoria.course.academy.owner == self.request.user

    def form_valid(self, form):
        enrollment = form.save(commit=False)
        enrollment.status = EnrollmentStatus.APPROVED
        enrollment.save()
        messages.success(self.request, "Inscripción aprobada.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("enrollments:academy_list")


class EnrollmentRejectView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Enrollment
    fields = []
    template_name = "enrollments/enrollment_confirm_reject.html"

    def test_func(self):
        enrollment = self.get_object()
        return enrollment.convocatoria.course.academy.owner == self.request.user

    def form_valid(self, form):
        enrollment = form.save(commit=False)
        enrollment.status = EnrollmentStatus.REJECTED
        enrollment.save()
        messages.success(self.request, "Inscripción rechazada.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("enrollments:academy_list")


class EnrollmentEnrollView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Enrollment
    fields = []
    template_name = "enrollments/enrollment_confirm_enroll.html"

    def test_func(self):
        enrollment = self.get_object()
        return enrollment.convocatoria.course.academy.owner == self.request.user

    def form_valid(self, form):
        enrollment = form.save(commit=False)
        enrollment.status = EnrollmentStatus.ENROLLED
        enrollment.save()
        messages.success(self.request, "Alumno matriculado.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("enrollments:academy_list")


class EnrollmentAnswerCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = EnrollmentAnswer
    form_class = EnrollmentAnswerForm
    template_name = "enrollments/answer_form.html"

    def get_enrollment(self):
        return get_object_or_404(Enrollment, pk=self.kwargs["enrollment_pk"])

    def test_func(self):
        enrollment = self.get_enrollment()
        return enrollment.student == self.request.user

    def form_valid(self, form):
        form.instance.enrollment = self.get_enrollment()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "enrollments:detail",
            kwargs={"pk": self.kwargs["enrollment_pk"]},
        )


class EnrollmentDocumentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = EnrollmentDocument
    form_class = EnrollmentDocumentForm
    template_name = "enrollments/document_form.html"

    def get_enrollment(self):
        return get_object_or_404(Enrollment, pk=self.kwargs["enrollment_pk"])

    def test_func(self):
        enrollment = self.get_enrollment()
        return enrollment.student == self.request.user

    def form_valid(self, form):
        form.instance.enrollment = self.get_enrollment()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "enrollments:detail",
            kwargs={"pk": self.kwargs["enrollment_pk"]},
        )


class EnrollmentDocumentVerifyView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = EnrollmentDocument
    fields = []
    template_name = "enrollments/document_confirm_verify.html"

    def test_func(self):
        document = self.get_object()
        return (
            document.enrollment.convocatoria.course.academy.owner
            == self.request.user
        )

    def form_valid(self, form):
        document = form.save(commit=False)
        document.is_verified = True
        document.save()
        messages.success(self.request, "Documento verificado.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "enrollments:detail",
            kwargs={"pk": self.object.enrollment.pk},
        )

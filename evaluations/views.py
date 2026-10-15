from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView

from enrollments.models import Enrollment

from .forms import EvaluationForm
from .models import Evaluation


class AcademyRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_academy


class EvaluationListView(AcademyRequiredMixin, ListView):
    model = Evaluation
    template_name = "evaluations/evaluation_list.html"
    context_object_name = "evaluations"

    def get_queryset(self):
        return Evaluation.objects.filter(
            enrollment__convocatoria__course__academy__owner=self.request.user
        ).select_related("enrollment", "enrollment__student")


class EvaluationCreateView(AcademyRequiredMixin, CreateView):
    model = Evaluation
    form_class = EvaluationForm
    template_name = "evaluations/evaluation_form.html"

    def get_enrollment(self):
        return get_object_or_404(Enrollment, pk=self.kwargs["enrollment_pk"])

    def form_valid(self, form):
        form.instance.enrollment = self.get_enrollment()
        form.instance.evaluated_by = self.request.user
        form.instance.evaluated_at = timezone.now()
        response = super().form_valid(form)
        messages.success(self.request, "Evaluación registrada.")
        return response

    def get_success_url(self):
        return reverse_lazy("evaluations:list")


class EvaluationUpdateView(AcademyRequiredMixin, UpdateView):
    model = Evaluation
    form_class = EvaluationForm
    template_name = "evaluations/evaluation_form.html"
    success_url = reverse_lazy("evaluations:list")

    def form_valid(self, form):
        form.instance.evaluated_by = self.request.user
        form.instance.evaluated_at = timezone.now()
        return super().form_valid(form)

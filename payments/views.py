import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView

from .forms import DiscountForm, PaymentForm, ScholarshipForm
from .models import Discount, Payment, Scholarship

logger = logging.getLogger(__name__)


class AcademyRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_academy


class DiscountListView(AcademyRequiredMixin, ListView):
    model = Discount
    template_name = "payments/discount_list.html"
    context_object_name = "discounts"


class DiscountCreateView(AcademyRequiredMixin, CreateView):
    model = Discount
    form_class = DiscountForm
    template_name = "payments/discount_form.html"
    success_url = reverse_lazy("payments:discount_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Descuento creado.")
        return response


class DiscountUpdateView(AcademyRequiredMixin, UpdateView):
    model = Discount
    form_class = DiscountForm
    template_name = "payments/discount_form.html"
    success_url = reverse_lazy("payments:discount_list")


class DiscountDeleteView(AcademyRequiredMixin, UpdateView):
    model = Discount
    form_class = DiscountForm
    template_name = "payments/discount_form.html"
    success_url = reverse_lazy("payments:discount_list")


class StudentScholarshipListView(LoginRequiredMixin, ListView):
    model = Scholarship
    template_name = "payments/scholarship_list.html"
    context_object_name = "scholarships"

    def get_queryset(self):
        return Scholarship.objects.filter(student=self.request.user)


class ScholarshipRequestView(LoginRequiredMixin, CreateView):
    model = Scholarship
    form_class = ScholarshipForm
    template_name = "payments/scholarship_form.html"

    def form_valid(self, form):
        form.instance.student = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Solicitud de beca enviada.")
        return response

    def get_success_url(self):
        return reverse_lazy("payments:scholarship_list")


class ScholarshipApproveView(AcademyRequiredMixin, UpdateView):
    model = Scholarship
    fields = ["amount"]
    template_name = "payments/scholarship_approve.html"

    def form_valid(self, form):
        scholarship = form.save(commit=False)
        scholarship.status = Scholarship.Status.APPROVED
        scholarship.reviewed_by = self.request.user
        scholarship.reviewed_at = timezone.now()
        scholarship.save()
        messages.success(self.request, "Beca aprobada.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("payments:scholarship_list")


class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = "payments/payment_list.html"
    context_object_name = "payments"

    def get_queryset(self):
        user = self.request.user
        if user.is_academy:
            return Payment.objects.filter(
                enrollment__convocatoria__course__academy__owner=user
            )
        return Payment.objects.filter(enrollment__student=user)


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = "payments/payment_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Pago registrado.")
        logger.info("Payment created: id=%s", self.object.pk)
        return response

    def get_success_url(self):
        return reverse_lazy("payments:payment_list")

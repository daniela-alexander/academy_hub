from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CompetenceForm, PassportEntryForm, TalentPassportForm
from .models import Competence, TalentPassport
from courses.models import Category


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class CompetenceListView(StaffRequiredMixin, ListView):
    model = Competence
    template_name = "talent/competence_list.html"
    context_object_name = "competences"
    paginate_by = 20

    def get_queryset(self):
        queryset = Competence.objects.filter(is_active=True).select_related("category")

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(name__icontains=query)

        category_id = self.request.GET.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["querystring"] = query_params.urlencode()
        return context



class CompetenceCreateView(StaffRequiredMixin, CreateView):
    model = Competence
    form_class = CompetenceForm
    template_name = "talent/competence_form.html"
    success_url = reverse_lazy("talent:competence_list")


class CompetenceUpdateView(StaffRequiredMixin, UpdateView):
    model = Competence
    form_class = CompetenceForm
    template_name = "talent/competence_form.html"
    success_url = reverse_lazy("talent:competence_list")


class MyPassportView(LoginRequiredMixin, DetailView):
    template_name = "talent/passport_detail.html"
    context_object_name = "passport"
    paginate_by = 20

    def get_object(self):
        passport, _ = TalentPassport.objects.get_or_create(
            student=self.request.user
        )
        return passport

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        entries = (
            self.object.entries
            .select_related("competence")
            .order_by("-obtained_at")
        )

        paginator = Paginator(entries, self.paginate_by)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        context["entries"] = page_obj.object_list

        return context


class MyPassportEditView(LoginRequiredMixin, UpdateView):
    model = TalentPassport
    form_class = TalentPassportForm
    template_name = "talent/passport_form.html"
    success_url = reverse_lazy("talent:passport")

    def get_object(self):
        passport, _ = TalentPassport.objects.get_or_create(
            student=self.request.user
        )
        return passport


class PassportEntryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    form_class = PassportEntryForm
    template_name = "talent/entry_form.html"

    def test_func(self):
        return self.request.user.is_academy

    def get_passport(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        student = get_object_or_404(User, pk=self.kwargs["student_pk"])
        passport, _ = TalentPassport.objects.get_or_create(student=student)
        return passport

    def form_valid(self, form):
        form.instance.passport = self.get_passport()
        response = super().form_valid(form)
        messages.success(self.request, "Competencia añadida al pasaporte.")
        return response

    def get_success_url(self):
        return reverse_lazy("talent:passport")

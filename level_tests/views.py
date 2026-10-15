from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.db.models import Q

from .forms import LevelTestAttemptForm, LevelTestForm
from .models import LevelTest, LevelTestAttempt


class AcademyRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_academy


class LevelTestListView(ListView):
    model = LevelTest
    template_name = "level_tests/level_test_list.html"
    context_object_name = "level_tests"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            LevelTest.objects
            .filter(is_active=True)
            .select_related("course", "course__academy")
)
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
)
        course_id = self.request.GET.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["querystring"] = query_params.urlencode()
        return context

class LevelTestDetailView(DetailView):
    model = LevelTest
    template_name = "level_tests/level_test_detail.html"
    context_object_name = "level_test"


class LevelTestCreateView(AcademyRequiredMixin, CreateView):
    model = LevelTest
    form_class = LevelTestForm
    template_name = "level_tests/level_test_form.html"
    success_url = reverse_lazy("level_tests:list")


class LevelTestUpdateView(AcademyRequiredMixin, UpdateView):
    model = LevelTest
    form_class = LevelTestForm
    template_name = "level_tests/level_test_form.html"
    success_url = reverse_lazy("level_tests:list")


class LevelTestAttemptView(LoginRequiredMixin, CreateView):
    model = LevelTestAttempt
    form_class = LevelTestAttemptForm
    template_name = "level_tests/attempt_form.html"

    def get_level_test(self):
        return get_object_or_404(LevelTest, pk=self.kwargs["pk"])

    def form_valid(self, form):
        form.instance.student = self.request.user
        form.instance.level_test = self.get_level_test()
        response = super().form_valid(form)
        messages.success(self.request, "Prueba de nivel registrada.")
        return response

    def get_success_url(self):
        return reverse_lazy("level_tests:list")

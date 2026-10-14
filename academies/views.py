import logging
from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from .forms import AcademyForm, TeacherForm
from .models import Academy, Teacher
logger = logging.getLogger(__name__)

class AcademyListView(ListView):
    model = Academy
    template_name = "academies/academy_list.html"
    context_object_name = "academies"
    paginate_by = 12
    def get_queryset(self):
        return (
            Academy.objects
            .filter(is_active=True)
            .select_related("owner")
)
    
class AcademyDetailView(DetailView):
    model = Academy
    template_name = "academies/academy_detail.html"
    context_object_name = "academy"

    def get_queryset(self):
        return (
            Academy.objects
            .select_related("owner")
            .prefetch_related("teachers", "courses")
)
    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        return queryset.get(slug=self.kwargs["slug"])
    
class AcademyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Academy
    form_class = AcademyForm
    template_name = "academies/academy_form.html"
    def test_func(self):
        return self.request.user.is_academy
    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Academia creada correctamente.")
        logger.info("Academy created: id=%s user=%s", self.object.pk, self.request.user.pk)
        return response
    
class AcademyOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        academy = self.get_object()
        return academy.owner == self.request.user
    
class AcademyUpdateView(AcademyOwnerMixin, UpdateView):
    model = Academy
    form_class = AcademyForm
    template_name = "academies/academy_form.html"
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Academia actualizada correctamente.")
        return response
    
class AcademyDeleteView(AcademyOwnerMixin, DeleteView):
    model = Academy
    template_name = "academies/academy_confirm_delete.html"
    success_url = reverse_lazy("academies:list")

class TeacherListView(ListView):
    model = Teacher
    template_name = "academies/teacher_list.html"
    context_object_name = "teachers"
    paginate_by = 12
    def get_queryset(self):
        return Teacher.objects.filter(is_active=True).select_related("academy")
    
class TeacherDetailView(DetailView):
    model = Teacher
    template_name = "academies/teacher_detail.html"
    context_object_name = "teacher"
    def get_queryset(self):
        return Teacher.objects.select_related("academy")
    
class TeacherCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = "academies/teacher_form.html"
    def test_func(self):
        return self.request.user.is_academy
    def get_academy(self):
        academy_pk = self.kwargs.get("academy_pk")
        return Academy.objects.get(pk=academy_pk)
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["academy"] = self.get_academy()
        return kwargs
    def test_func(self):
        academy = self.get_academy()
        return (
            self.request.user.is_academy
            and academy.owner == self.request.user
        )
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Profesor creado correctamente.")
        return response
    def get_success_url(self):
        return reverse_lazy(
            "academies:detail",
            kwargs={"slug": self.object.academy.slug},
        )
    
class TeacherOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        teacher = self.get_object()
        return teacher.academy.owner == self.request.user
    
class TeacherUpdateView(TeacherOwnerMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = "academies/teacher_form.html"
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["academy"] = self.object.academy
        return kwargs
    
class TeacherDeleteView(TeacherOwnerMixin, DeleteView):
    model = Teacher
    template_name = "academies/teacher_confirm_delete.html"
    def get_success_url(self):
        return reverse_lazy(
            "academies:detail",
            kwargs={"slug": self.object.academy.slug},
        ) 
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

from .forms import (
    CategoryForm,
    ConvocatoriaForm,
    CourseForm,
    CourseImageForm,
)
from .models import (
    Category,
    Convocatoria,
    Course,
    CourseImage,
    CourseStatus,
)

logger = logging.getLogger(__name__)


class CourseListView(ListView):
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    paginate_by = 12

    def get_queryset(self):
        return (
            Course.objects
            .filter(status=CourseStatus.PUBLISHED)
            .select_related("academy", "category", "teacher")
        )


class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"

    def get_queryset(self):
        return (
            Course.objects
            .select_related("academy", "category", "teacher")
            .prefetch_related("images", "convocatorias")
        )

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        return queryset.get(pk=self.kwargs["pk"], slug=self.kwargs["slug"])


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def test_func(self):
        return self.request.user.is_academy and self.request.user.academies.exists()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.status = CourseStatus.PUBLISHED
        response = super().form_valid(form)
        messages.success(self.request, "Curso publicado correctamente.")
        logger.info("Course created: id=%s user=%s", self.object.pk, self.request.user.pk)
        return response


class CourseOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        course = self.get_object()
        return course.academy.owner == self.request.user


class CourseUpdateView(CourseOwnerMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Curso actualizado correctamente.")
        return response


class CourseDeleteView(CourseOwnerMixin, DeleteView):
    model = Course
    template_name = "courses/course_confirm_delete.html"
    success_url = reverse_lazy("courses:list")


class MyCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "courses/my_course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        return (
            Course.objects
            .filter(academy__owner=self.request.user)
            .select_related("academy", "category", "teacher")
        )


class CategoryListView(ListView):
    model = Category
    template_name = "courses/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class CategoryDetailView(DetailView):
    model = Category
    template_name = "courses/category_detail.html"
    context_object_name = "category"

    def get_object(self, queryset=None):
        queryset = queryset or Category.objects.all()
        return queryset.get(slug=self.kwargs["slug"])


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_staff


class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "courses/category_form.html"
    success_url = reverse_lazy("courses:category_list")


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "courses/category_form.html"
    success_url = reverse_lazy("courses:category_list")


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = "courses/category_confirm_delete.html"
    success_url = reverse_lazy("courses:category_list")


class ConvocatoriaCreateView(CourseOwnerMixin, CreateView):
    model = Convocatoria
    form_class = ConvocatoriaForm
    template_name = "courses/convocatoria_form.html"

    def get_course(self):
        return Course.objects.get(pk=self.kwargs["course_pk"])

    def test_func(self):
        course = self.get_course()
        return course.academy.owner == self.request.user

    def form_valid(self, form):
        form.instance.course = self.get_course()
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class ConvocatoriaOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        convocatoria = self.get_object()
        return convocatoria.course.academy.owner == self.request.user


class ConvocatoriaUpdateView(ConvocatoriaOwnerMixin, UpdateView):
    model = Convocatoria
    form_class = ConvocatoriaForm
    template_name = "courses/convocatoria_form.html"

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class ConvocatoriaDeleteView(ConvocatoriaOwnerMixin, DeleteView):
    model = Convocatoria
    template_name = "courses/convocatoria_confirm_delete.html"

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class CourseImageCreateView(CourseOwnerMixin, CreateView):
    model = CourseImage
    form_class = CourseImageForm
    template_name = "courses/course_image_form.html"

    def get_course(self):
        return Course.objects.get(pk=self.kwargs["course_pk"])

    def test_func(self):
        course = self.get_course()
        return course.academy.owner == self.request.user

    def form_valid(self, form):
        form.instance.course = self.get_course()
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class CourseImageOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        image = self.get_object()
        return image.course.academy.owner == self.request.user


class CourseImageUpdateView(CourseImageOwnerMixin, UpdateView):
    model = CourseImage
    form_class = CourseImageForm
    template_name = "courses/course_image_form.html"

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class CourseImageDeleteView(CourseImageOwnerMixin, DeleteView):
    model = CourseImage
    template_name = "courses/course_image_confirm_delete.html"

    def get_success_url(self):
        return self.object.course.get_absolute_url()

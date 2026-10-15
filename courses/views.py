import logging

from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
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
    CourseFavorite,
    CourseImage,
    CourseLevel,
    CourseModality,
    CourseStatus,
)

logger = logging.getLogger(__name__)

class CourseListView(ListView):
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Course.objects
            .filter(status=CourseStatus.PUBLISHED)
            .select_related("academy", "category", "teacher")
            .prefetch_related("images", "convocatorias")
        )

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(objectives__icontains=query)
                | Q(competences__icontains=query)
                | Q(academy__name__icontains=query)
                | Q(category__name__icontains=query)
            )

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category__slug=category)

        academy = self.request.GET.get("academy")
        if academy:
            queryset = queryset.filter(academy__slug=academy)

        level = self.request.GET.get("level")
        if level and level in CourseLevel.values:
            queryset = queryset.filter(level=level)

        modality = self.request.GET.get("modality")
        if modality and modality in CourseModality.values:
            queryset = queryset.filter(modality=modality)

        min_price = self._parse_decimal("min_price")
        max_price = self._parse_decimal("max_price")

        if min_price is not None:
            queryset = queryset.filter(
                convocatorias__price__gte=min_price,
                convocatorias__is_active=True,
            )
        if max_price is not None:
            queryset = queryset.filter(
                convocatorias__price__lte=max_price,
                convocatorias__is_active=True,
            )

        ordering_map = {
            "newest": "-created_at",
            "oldest": "created_at",
            "price_asc": "min_price",
            "price_desc": "-min_price",
            "popular": "-views_count",
        }
        ordering = self.request.GET.get("ordering", "newest")
        queryset = queryset.order_by(ordering_map.get(ordering, "-created_at"))

        return queryset.distinct()

    def _parse_decimal(self, key):
        from decimal import Decimal, InvalidOperation
        raw = self.request.GET.get(key)
        if not raw:
            return None
        try:
            return Decimal(raw)
        except (InvalidOperation, ValueError):
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        context["levels"] = CourseLevel.choices
        context["modalities"] = CourseModality.choices

        context["favorite_course_ids"] = set()
        if self.request.user.is_authenticated:
            context["favorite_course_ids"] = set(
                CourseFavorite.objects
                .filter(user=self.request.user)
                .values_list("course_id", flat=True)
            )

        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["querystring"] = query_params.urlencode()

        return context


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def test_func(self):
        return (
            self.request.user.is_academy
            and self.request.user.academies.exists()
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.status = CourseStatus.PUBLISHED

        with transaction.atomic():
            response = super().form_valid(form)

            images = form.cleaned_data.get("images") or []
            for position, image in enumerate(images):
                CourseImage.objects.create(
                    course=self.object,
                    image=image,
                    is_primary=(position == 0),
                    position=position,
                )

        messages.success(self.request, "Curso publicado correctamente.")
        logger.info(
            "Course created: id=%s user=%s",
            self.object.pk,
            self.request.user.pk,
        )
        return response


@login_required
@require_POST
def toggle_course_favorite(request, pk):
    course = get_object_or_404(
        Course,
        pk=pk,
        status=CourseStatus.PUBLISHED,
    )

    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = course.get_absolute_url()

    if course.academy.owner_id == request.user.pk:
        messages.warning(
            request,
            "No puedes guardar tu propio curso.",
        )
        return redirect(next_url)

    with transaction.atomic():
        favorite, created = CourseFavorite.objects.get_or_create(
            user=request.user,
            course=course,
        )
        if not created:
            favorite.delete()
            messages.info(request, "Curso eliminado de favoritos.")
        else:
            messages.success(request, "Curso añadido a favoritos.")

    return redirect(next_url)


class CourseFavoriteListView(LoginRequiredMixin, ListView):
    model = CourseFavorite
    template_name = "courses/course_favorite_list.html"
    context_object_name = "favorites"
    paginate_by = 12

    def get_queryset(self):
        return (
            CourseFavorite.objects
            .filter(user=self.request.user)
            .select_related(
                "course",
                "course__academy",
                "course__category",
                "course__teacher",
            )
            .prefetch_related("course__images")
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
        course = queryset.get(pk=self.kwargs["pk"], slug=self.kwargs["slug"])

        Course.objects.filter(pk=course.pk).update(
            views_count=F("views_count") + 1
        )
        course.refresh_from_db(fields=["views_count"])
        return course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_favorite"] = False

        if self.request.user.is_authenticated:
            context["is_favorite"] = CourseFavorite.objects.filter(
                user=self.request.user,
                course=self.object,
            ).exists()

        context["favorite_count"] = self.object.favorites.count()

        return context


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

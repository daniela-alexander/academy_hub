import logging

from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import AcademyForm, TeacherForm
from .models import Academy, AcademyFavorite, Teacher

logger = logging.getLogger(__name__)


# ============================================================
# ACADEMY
# ============================================================

class AcademyListView(ListView):
    model = Academy
    template_name = "academies/academy_list.html"
    context_object_name = "academies"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Academy.objects
            .filter(is_active=True)
            .select_related("owner")
            .prefetch_related("courses")
        )

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(city__icontains=query)
            )

        city = self.request.GET.get("city")
        if city:
            queryset = queryset.filter(city__icontains=city)

        ordering_map = {
            "newest": "-created_at",
            "name_asc": "name",
            "name_desc": "-name",
            "popular": "-views_count",
        }
        ordering = self.request.GET.get("ordering", "newest")
        queryset = queryset.order_by(ordering_map.get(ordering, "-created_at"))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["favorite_academy_ids"] = set()
        if self.request.user.is_authenticated:
            context["favorite_academy_ids"] = set(
                AcademyFavorite.objects
                .filter(user=self.request.user)
                .values_list("academy_id", flat=True)
            )

        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["querystring"] = query_params.urlencode()

        return context


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
        academy = queryset.get(slug=self.kwargs["slug"])

        Academy.objects.filter(pk=academy.pk).update(
            views_count=F("views_count") + 1
        )
        academy.refresh_from_db(fields=["views_count"])
        return academy

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["is_favorite"] = False
        if self.request.user.is_authenticated:
            context["is_favorite"] = AcademyFavorite.objects.filter(
                user=self.request.user,
                academy=self.object,
            ).exists()

        context["favorite_count"] = self.object.favorites.count()
        return context


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
        logger.info(
            "Academy created: id=%s user=%s",
            self.object.pk,
            self.request.user.pk,
        )
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


class AcademyFavoriteListView(LoginRequiredMixin, ListView):
    model = AcademyFavorite
    template_name = "academies/academy_favorite_list.html"
    context_object_name = "favorites"
    paginate_by = 12

    def get_queryset(self):
        return (
            AcademyFavorite.objects
            .filter(user=self.request.user)
            .select_related("academy", "academy__owner")
        )


@login_required
@require_POST
def toggle_academy_favorite(request, slug):
    academy = get_object_or_404(Academy, slug=slug, is_active=True)

    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse("academies:detail", kwargs={"slug": academy.slug})

    if academy.owner_id == request.user.pk:
        messages.warning(request, "No puedes guardar tu propia academia.")
        return redirect(next_url)

    with transaction.atomic():
        favorite, created = AcademyFavorite.objects.get_or_create(
            user=request.user,
            academy=academy,
        )
        if not created:
            favorite.delete()
            messages.info(request, "Academia eliminada de favoritos.")
        else:
            messages.success(request, "Academia añadida a favoritos.")

    return redirect(next_url)


# ============================================================
# TEACHER
# ============================================================

class TeacherListView(ListView):
    model = Teacher
    template_name = "academies/teacher_list.html"
    context_object_name = "teachers"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Teacher.objects
            .filter(is_active=True)
            .select_related("academy")
        )

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(specialty__icontains=query)
            )

        academy_id = self.request.GET.get("academy")
        if academy_id:
            queryset = queryset.filter(academy_id=academy_id)

        return queryset.order_by("last_name", "first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["querystring"] = query_params.urlencode()
        return context

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

    def get_academy(self):
        academy_pk = self.kwargs.get("academy_pk")
        return get_object_or_404(Academy, pk=academy_pk)

    def test_func(self):
        academy = self.get_academy()
        return (
            self.request.user.is_academy
            and academy.owner == self.request.user
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["academy"] = self.get_academy()
        return kwargs

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
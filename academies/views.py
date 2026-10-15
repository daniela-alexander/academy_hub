from django.db.models import F, Q
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Academy, AcademyFavorite, Teacher
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

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
import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

from .forms import ProfileForm, RegisterForm

User = get_user_model()
logger = logging.getLogger(__name__)

def register(request):

    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            messages.success(
                request,
                "Cuenta creada correctamente.",
            )

            return redirect("accounts:profile")

    else:
        form = RegisterForm()

    logger.info(
        "New user registered: %s",
        request.user.username,
    )

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )

@login_required
def profile(request):

    return render(
        request,
        "accounts/profile.html",
    )

@login_required
def profile_edit(request):

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Perfil actualizado correctamente.",
            )

            return redirect("accounts:profile")

    else:

        form = ProfileForm(
            instance=request.user
        )

    return render(
        request,
        "accounts/profile_edit.html",
        {"form": form},
    )

class UserPublicProfileView(DetailView):
    model = User
    template_name = "accounts/public_profile.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_queryset(self):
        return User.objects.filter(is_active=True)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_staff


class UserListView(StaffRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.all().order_by("-created_at")
        q = self.request.GET.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q)
                | Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
            )
        role = self.request.GET.get("role")
        if role == "academy":
            queryset = queryset.filter(is_academy=True)
        elif role == "student":
            queryset = queryset.filter(is_student=True)
        elif role == "staff":
            queryset = queryset.filter(is_staff=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        querystring = self.request.GET.copy()
        if "page" in querystring:
            querystring.pop("page")
        context["querystring"] = querystring.urlencode()
        return context

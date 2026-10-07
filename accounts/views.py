from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
import logging

from .forms import ProfileForm, RegisterForm

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
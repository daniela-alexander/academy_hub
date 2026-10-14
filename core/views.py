from django.shortcuts import render
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

from .forms import ContactMessageForm
from .models import ContactMessage



def home(request):
    return render(request, "core/home.html")

def about(request):
    return render(request, "core/about.html")

class ContactMessageCreateView(CreateView):
    model = ContactMessage
    form_class = ContactMessageForm
    template_name = "core/contact_form.html"
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Mensaje enviado correctamente. Gracias por contactarnos.",
        )
        return super().form_valid(form)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_staff


class ContactMessageListView(StaffRequiredMixin, ListView):
    model = ContactMessage
    template_name = "core/contact_message_list.html"
    context_object_name = "messages_list"
    paginate_by = 20

    def get_queryset(self):
        return ContactMessage.objects.all().order_by("-created_at")


class ContactMessageDetailView(StaffRequiredMixin, DetailView):
    model = ContactMessage
    template_name = "core/contact_message_detail.html"
    context_object_name = "contact_message"


class ContactMessageUpdateView(StaffRequiredMixin, UpdateView):
    model = ContactMessage
    fields = ["is_read"]
    template_name = "core/contact_message_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "core:contact_message_detail",
            kwargs={"pk": self.object.pk},
        )


class ContactMessageDeleteView(StaffRequiredMixin, DeleteView):
    model = ContactMessage
    template_name = "core/contact_message_confirm_delete.html"
    success_url = reverse_lazy("core:contact_message_list")

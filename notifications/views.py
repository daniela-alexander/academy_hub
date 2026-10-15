from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)

        is_read = self.request.GET.get("is_read")
        if is_read == "1":
            queryset = queryset.filter(is_read=True)
        elif is_read == "0":
            queryset = queryset.filter(is_read=False)

        notification_type = self.request.GET.get("type")
        if notification_type:
            queryset = queryset.filter(type=notification_type)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["types"] = Notification.Type.choices
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["querystring"] = query_params.urlencode()
        return context


def mark_as_read(request, pk):
    notification = get_object_or_404(
        Notification, pk=pk, user=request.user
    )
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
    return redirect("notifications:list")


def mark_all_as_read(request):
    Notification.objects.filter(
        user=request.user, is_read=False
    ).update(is_read=True, read_at=timezone.now())
    return redirect("notifications:list")

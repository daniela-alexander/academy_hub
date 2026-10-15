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
        return Notification.objects.filter(user=self.request.user)


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

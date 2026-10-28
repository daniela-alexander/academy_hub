# Separado de views.py (REST) para no mezclar.

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView

from .models import Conversation, Participant
from .services import (
    create_direct_conversation,
    create_group_conversation,
    mark_messages_as_read,
    send_message,
)

User = get_user_model()


class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = "chat/conversation_list.html"
    context_object_name = "conversations"

    def get_queryset(self):
        return (
            Conversation.objects
            .filter(participants__user=self.request.user)
            .prefetch_related("participants__user")
            .distinct()
            .order_by("-updated_at")
        )


class ConversationDetailView(LoginRequiredMixin, View):
    template_name = "chat/conversation_detail.html"

    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)

        if not Participant.objects.filter(
            conversation=conversation, user=request.user
        ).exists():
            raise PermissionDenied("No participas en esta conversación.")

        mark_messages_as_read(conversation.pk, request.user)

        messages_qs = (
            conversation.messages
            .select_related("sender")
            .order_by("created_at")
        )

        return render(
            request,
            self.template_name,
            {
                "conversation": conversation,
                "messages": messages_qs,
                "is_group": conversation.is_group,
            },
        )

    def post(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)

        try:
            send_message(request.user, conversation.pk, request.POST.get("text", ""))
            messages.success(request, "Mensaje enviado.")
        except (ValidationError, PermissionDenied) as e:
            messages.error(request, str(e))

        return redirect("chat:detail", pk=pk)


class CreateGroupView(LoginRequiredMixin, View):
    template_name = "chat/create_group.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        title = request.POST.get("title", "").strip()
        usernames = request.POST.getlist("participants")
        participant_ids = []

        for username in usernames:
            try:
                u = User.objects.get(username=username)
                participant_ids.append(u.pk)
            except User.DoesNotExist:
                messages.warning(
                    request, f"Usuario '{username}' no encontrado."
                )

        try:
            conversation = create_group_conversation(
                creator=request.user,
                title=title,
                participant_ids=participant_ids,
            )
            messages.success(request, "Grupo creado.")
            return redirect("chat:detail", pk=conversation.pk)
        except (ValidationError, PermissionDenied) as e:
            messages.error(request, str(e))
            return render(request, self.template_name)


class CreateDirectConversationView(LoginRequiredMixin, View):

    def post(self, request):
        username = request.POST.get("username", "").strip()

        try:
            other = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, f"Usuario '{username}' no encontrado.")
            return redirect("chat:list")

        try:
            conversation = create_direct_conversation(
                user_a=request.user,
                user_b=other,
            )
            return redirect("chat:detail", pk=conversation.pk)
        except (ValidationError, PermissionDenied) as e:
            messages.error(request, str(e))
            return redirect("chat:list")

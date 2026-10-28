from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Participant


class IsParticipant(BasePermission):
    """
    Solo los participantes de la conversación pueden verla o escribir en ella.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return Participant.objects.filter(
            conversation=obj,
            user=request.user,
        ).exists()

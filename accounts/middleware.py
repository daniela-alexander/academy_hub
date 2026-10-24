from .presence import mark_user_online, update_last_seen


class UserPresenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                mark_user_online(request.user.pk)
                update_last_seen(request.user.pk)
            except Exception:
                # Redis caído: no rompemos la petición
                pass

        return self.get_response(request)

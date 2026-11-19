from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AdminBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username and '@' in username and not User.objects.filter(username=username).exists():
            matches = list(User.objects.filter(email__iexact=username,is_superuser=True).values_list('username',flat=True)[:2])
            if len(matches) == 1:
                username = matches[0]
        user = super().authenticate(request, username, password, **kwargs)
        return user if user and user.is_superuser else None

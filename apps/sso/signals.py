from apps.sso.models import ApplicationConsent
from oauth2_provider.signals import app_authorized


def handle_app_authorized(sender, request, token, **kwargs):
    if ApplicationConsent.objects.filter(pk=token.application.pk).exists():
        return
    ApplicationConsent.objects.create(
        user=token.user, client=token.application, approved_scopes=token.scopes
    )


app_authorized.connect(handle_app_authorized)
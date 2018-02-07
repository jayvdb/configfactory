from configfactory.models.api_settings import APISettings


def generate_api_token() -> str:
    from django.utils.crypto import get_random_string
    while True:
        token = get_random_string(48)
        if not APISettings.objects.filter(token=token).exists():
            return token

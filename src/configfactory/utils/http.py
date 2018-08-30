def query_params(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = str(v)
    return updated.urlencode()


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

import configfactory


def version(request):
    return {
        'version': configfactory.__version__
    }


def auth(request):
    return {
        'current_user':  request.user
    }


def components(request):
    return {
        'components': request.components,
    }


def environments(request):
    return {
        'view_environments': request.view_environments,
        'change_environments': request.change_environments,
    }

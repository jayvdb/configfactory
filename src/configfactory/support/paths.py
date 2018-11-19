import os


def root_path(path: str = None) -> str:
    """
    Returns root path.
    """
    up = os.path.dirname
    root = up(up(up(up(__file__))))
    return _join_path(root, path)


def app_path(path: str = None) -> str:
    """
    Return application package path.
    """
    up = os.path.dirname
    root = up(up(__file__))
    return _join_path(root, path)


def var_path(path: str = None) -> str:
    return _join_path(root_path('var'), path)


def _join_path(root: str, path: str = None) -> str:
    if path:
        return os.path.join(root, path)
    return root

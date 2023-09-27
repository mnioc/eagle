from typing import Callable


def shared_context(handler: Callable, context_key):
    """
    Decorator for setting shared context to test case.
    Args:
        handler (Callable): A callable object that returns a context.
        context_key (str): The key of context.
    Returns:
        Callable: A decorator.

    Usage:

        >>> from eagle.testcase.context import shared_context

        >>> def handler():
                return 3

        >>> @shared_context(handler, pk)
            class A:
                ...

        >>> A().pk
        3

    In this example, with the decorator, the context_key(pk) of A is set to 3.
    """
    if not callable(handler):
        raise TypeError(f'handler must be callable, got {type(handler)}')

    def decorator(obj):

        if not isinstance(obj, type):
            raise TypeError(f'obj must be a type, got {type(obj)}')

        def set_context_to(*args, **kwargs):
            setattr(obj, context_key, handler())
            return obj

        return set_context_to

    return decorator


class CallAPIHandler:
    """
    Handler for call API.
    """

    def __init__(self, url, method, client):
        ...

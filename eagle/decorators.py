import functools
import inspect

def find_class_of_function(func):
    module = inspect.getmodule(func)
    print(inspect.getmembers(module))
    return next(
        (
            print(obj)
            for name, obj in inspect.getmembers(module)
            if inspect.isclass(obj) and func.__name__ in dir(obj)
        ),
        None,
    )


def auto_generate_use_case(
    method: str,
    url: str,
    payload: dict,
    response_hooks: dict
):
    def warp(func):
        print(find_class_of_function(func))
        print(func.__class__)
        raise Exception('test')
        @functools.wraps(func)
        def decor(*args, **kwargs):
            return func(*args, **kwargs)
        return decor
    return warp

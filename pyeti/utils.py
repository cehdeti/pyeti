try:
    from django.utils import six
except ImportError:
    import six


class empty_context(object):
    """
    A silly little context manager that essentially does nothing. Useful with
    conditional `with` statements:

        ```
        with transaction.atomic() if transact else empty_context():
            ...
        ```
    """

    def __enter__(self):
        return None

    def __exit__(self, *_):
        return False

    def __call__(self):
        return self

empty_context = empty_context()


def ignore_exception(*exception_classes):
    """
    A function decorator to catch exceptions and pass.

        @ignore_exception(ValueError, ZeroDivisionError)
        def my_function():
            ...

    Note that this functionality should only be used when you don't care about
    the return value of the function, as it will return `None` if an exception
    is caught.
    """
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (exception_classes):
                pass
        return func_wrapper
    return decorator


def is_truthy(value):
    """
    Utility function that converts various values to a boolean. Useful for web
    requests, where the value that comes in may be "0" or "false", etc.
    """
    if isinstance(value, six.string_types) and value.lower() in ('false', '0'):
        return False
    else:
        return bool(value)

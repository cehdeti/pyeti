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


def ignore_exception(*exception_classes):
    """
    A function decorator to catch exceptions and pass.

        @ignore_exception(ValueError, ZeroDivisionError)
        def my_function():
            ...
    """
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (exception_classes):
                pass
        return func_wrapper
    return decorator

from six.moves import input


def confirm(message, default=None):
    """
    Ask the user a question, then wait for a yes or no answer. Returns the
    boolean result.
    """
    result = input(message)

    if not result and default is not None:
        return default

    while len(result) < 1 or result.lower() not in "yn":
        result = input("Please answer yes or no: ")
    return result[0].lower() == "y"

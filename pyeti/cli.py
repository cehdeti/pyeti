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


def required_input(message):
    """
    Collect input from user and repeat until they answer.
    """
    result = input(message)

    while len(result) < 1:
        result = input(message)

    return result


def password_confirm(message='Password: ',
                     confirm_message='Confirm password: '):
    """
    Prompt the user for a password and confirmation. Returns the password if
    they match, `False` if they don't.
    """
    password = required_input(message)
    confirm = required_input(confirm_message)

    if password == confirm:
        return password
    else:
        return False

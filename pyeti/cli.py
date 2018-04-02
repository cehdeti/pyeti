from six.moves import input
from getpass import getpass


def confirm(message, default=None):
    """
    Ask the user a question, then wait for a yes or no answer. Returns the
    boolean result.
    """
    result = input(message)

    if not result and default is not None:
        return default

    while len(result) < 1 or result.lower() not in 'yn':
        result = input('Please answer yes or no: ')
    return result[0].lower() == 'y'


def required_input(message, method=input):
    """
    Collect input from user and repeat until they answer.
    """
    result = method(message)

    while len(result) < 1:
        result = method(message)

    return result


def password_confirm(message='Password: ',
                     confirm_message='Confirm password: '):
    """
    Prompt the user for a password and confirmation. Returns the password if
    they match, `False` if they don't.
    """
    password = required_input(message, method=getpass)
    confirm = required_input(confirm_message, method=getpass)

    if password == confirm:
        return password
    else:
        return False


def prompt(choices, label):
    """
    Prompt the user to choose an item from the list. Options should be a list
    of 2-tuples, where the first item is the value to be returned when the
    option is selected, and the second is the label that will be displayed to the
    user.
    """
    lines = ['%d) %s' % (i + 1, item[1]) for i, item in enumerate(choices)]
    index = input('\n'.join(lines + ['', 'Please select a %s: ' % label]))
    while len(index) < 1 or int(index) < 1 or int(index) > len(choices):
        index = input('Please enter a valid choice: ')
    return choices[int(index) - 1][0]

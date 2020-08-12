import os
import re

from django.conf import settings
from django.template.loaders.app_directories import get_app_template_dirs

placeholder_re = re.compile(r"{% placeholder\s+('|\")(?P<name>[^\1]+?)\1[^}]+%}")


def get_placeholders():
    placeholders = set()
    for template_dir in (settings.TEMPLATES[0].get('DIRS', tuple()) + get_app_template_dirs('templates')):
        for dirname, dirnames, filenames in os.walk(template_dir):
            for filename in filenames:
                with open(os.path.join(dirname, filename)) as file_:
                    for line in file_:
                        placeholders.update(parse_placeholders(line))
    return placeholders


def parse_placeholders(string):
    """
    Given a string, return a list of `{% placeholder %}` tags found.
    """
    return [m.group('name') for m in placeholder_re.finditer(string)]

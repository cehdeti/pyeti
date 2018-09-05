from dateutil import parser
from django.utils import timezone


def parse_spree_date(string):
    return parser.parse(string)


def difference_in_days(string):
    return (parse_spree_date(string) - timezone.now()).days

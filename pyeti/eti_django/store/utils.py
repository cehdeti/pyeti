from dateutil import parser
from django.utils import timezone


parse_spree_date = parser.parse
parse_spree_datetime = parser.parse


def difference_in_days(string):
    return (parse_spree_date(string) - timezone.now()).days

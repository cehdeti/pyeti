from dateutil import parser
from datetime import datetime


def parse_spree_date(string):
    return parser.parse(string, ignoretz=True)


def difference_in_days(string):
    then = parse_spree_date(string)
    now = datetime.now()
    return (then - now).days

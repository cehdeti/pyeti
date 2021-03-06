from datetime import date, timedelta


def enumerate_days(start, end=None):
    if end is None:
        end = date.today()
    day = timedelta(days=1)
    while start <= end:
        yield start
        start += day

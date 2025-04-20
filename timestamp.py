from datetime import datetime


def extract_ymd(t):
    """
    Parse a datetime string in ISO 8601 format and return a tuple.
    """

    dt = datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")

    year = str(dt.year)
    month = f"{dt.month:02}"
    day = f"{dt.day:02}"

    return (year, month, day)

import re
import logging
from dateutil.parser import parse

operators = {
    "=": "eq",
    ">=": "ge",
    "<=": "le",
    "&": "and",
    "||": "or"
}


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

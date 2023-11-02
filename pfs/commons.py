from datetime import datetime
from dateutil.parser import parse
import ast

operators = {
    "=": "eq",
    ">=": "ge",
    "<=": "le",
    "&": "and",
    "||": "or"
}


# Function to reformat the experiment name, for example, if users input cba glucose tolerance test,
# it will return CBA_GLUCOSE_TOLERANCE_TEST
def format_experiment_name(name: str):
    return name.replace(" ", "_").upper()


# Function to check whether an input is a date
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


# Define a function called convert_string_to_bool that takes a string as input.
def convert_string_to_bool(str_value):
    try:
        # Use the ast.literal_eval function to safely evaluate the input string.
        value = ast.literal_eval(str_value)
    except (SyntaxError, ValueError):
        # If an error occurs during evaluation, return False.
        return False
    # Convert the evaluated value to a boolean using the bool function.
    # Return the boolean value.
    return bool(value)


# Function to convert
def to_odata_operator(operator):
    try:
        return operators[operator]
    except KeyError as e:
        raise KeyError()


# Function to auto-generate the odata filtering query from lists of input.
def generate_filter_str(filter_by) -> str:
    try:
        words = filter_by.split(" ")
        var, operator = words[0], words[1]
        val = words[2] + " " + words[3] if len(words) == 4 else words[2]
        if isinstance(val, str):
            if is_date(val):
                val = datetime.strptime(val, '%Y-%m-%d').date()
            elif val.isdigit():
                val = int(val)
            elif val == "True" or val == "False":
                val = bool(val)
            else:
                val = f"'{val}'"

        filter_str = f"{var} {operators[operator]} {val}"
        return filter_str

    except AssertionError as e:
        pass


def generate_orderby_str(order_by: tuple):
    return f"{order_by[0]} {order_by[1]}"


# Dict to translate user input entity type name to key value in the json data
entityTypeName = {
    "SAMPLE": "MOUSE_SAMPLE",
    "SAMPLE_LOT": "MOUSE_SAMPLE_LOT"
}

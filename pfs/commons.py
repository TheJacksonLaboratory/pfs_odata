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

sample_attribute_dict = {
    "entitytypename": "entity_type",
    "id": "id",
    "name": "name",
    "barcode": "barcode",
    "sequence": "sequence",
    "created": "date_created",
    "modified": "date_modified",
    "active": "active",
    "likedby": "likeby",
    "followedby": "followedby",
    "locked": "locked",
    "jax_mousesample_treatmentgroup": "treatment_group",
    "jax_mousesample_dietgraintype": "diet",
    "jax_mousesample_bedding": "bedding",
    "jax_mousesample_isalive": "received_alive",
    "jax_mousesample_isfiller": "filler_mouse",
    "jax_mousesample_accomodation": "accomodation",
    "jax_sample_currentclinicalobs": "current_clinical_observation",
    "jax_mousesample_anticipatedphenotype": "anticipated_clinical_observation",
    "jax_mousesample_additionalinformation": "additional_notes",
    "jax_mousesample_immunosufficiency": "immune_status",
    "jax_sample_externalid": "customer_mouse_id",
    "jax_mousesample_litternumber": "litter_number",
    "jax_mousesample_primaryid": "primary_id",
    "jax_mousesample_primaryidvalue": "primary_id_value",
    "jax_mousesample_secondaryid": "secondary_id",
    "jax_mousesample_secondaryidvalue": "secondary_id_value",
    "jax_sample_cohortname": "cohort_name",
    "jax_mousesample_blindid": "blind_id",
    "jax_mousesample_mepid": "mep_id",
    "jax_mousesample_nbpid": "nbp_group_id",
    "jax_mousesample_pooledrole": "role",
    "jax_mousesample_sourcepenid": "source_pen_id",
    "jax_mousesample_sex": "sex",
    "jax_sample_mousecolonyroom": "mouse_room_of_origin",
    "jax_sample_mouseroomsection": "section_of_origin",
    "jax_mousesample_dateofbirth": "dob",
    "jax_sample_comments": "comments",
    "jax_mousesample_dateofdeath": "dod",
    "jax_mousesample_reasonfordeath": "reason_for_death",
    "jax_mousesample_usersdefinedstrainname": "user_defined_strain_name",
    "jax_mousesample_allele": "allele",
    "jax_mousesample_genotype": "genotype",
    "jax_mousesample_coatcolor": "coat_color",
    "jax_mousesample_pedigree": "pedigree",
    "jax_mousesample_wholemousefail": "whole_mouse_fail",
    "jax_mousesample_wholemousefailreasons": "failed_reason",
    "jax_mousesample_wholemousefailexplanation": "explanation",
    "jax_mousesample_lotreport": "lot_report",
    "jax_uuid_useforname": "use_for_mouse_name",
    "jax_mousesample_mousemanifestversion": "mouse_manifest_version",
    "jax_mousesample_activestatusversiontracker": "active_status_tracker",
    "jax_mousesample_exitreason": "exit_reason"
}

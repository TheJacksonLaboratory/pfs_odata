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


sample_attribute_dict = {
    "entitytypename": "entity_type",
    "id": "id",
    "name": "name",
    "barcode": "barcode",
    "created": "data_created",
    "modified": "date_modified",
    "active": "active",
    "likedby": "likeby",
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
    "jax_mousesample_mepid": "MEP_id",
    "jax_mousesample_nbpid": "NBP_group_id",
    "jax_mousesample_pooledrole": "role",
    "jax_mousesample_sourcepenid": "source_pen_id",
    "jax_mousesample_sex": "sex",
    "jax_sample_mousecolonyroom": "mouse_room_of_origin",
    "jax_sample_mouseroomsection": "section_of_origin",
    "jax_mouseSample_dateofbirth": "date_of_birth",
    "jax_sample_comments": "comments",
    "jax_mousesample_dateofdeath": "date_of_death",
    "jax_mousesample_reasonfordeath": "reason_for_death:",
    "jax_mousesample_usersdefinedstrainname": "user_defined_strain_name:",
    "jax_mousesample_genotype": "genotype",
    "jax_mousesample_coatcolor": "coat_color",
    "jax_mousesample_pedigree:": "pedigree",
    "jax_mousesample_wholemousefail": "whole_mouse_fail",
    "jax_mousesample_wholemousefailreasons": "fail_reason",
    "jax_mousesample_wholemousefailexplanation": "explanation",
    "jax_mousesample_lotreport": "lot_report",
    "jax_uuid_useforname": "use_for_mouse_name",
    "jax_mousesample_mousemanifestversion": "mouse_manifest_version",
    "jax_mousesample_activestatusversiontracker": "active_status_tracker"
}

sample_lot_attribute_dict = {

}



"""
TODO Nov 2nd:
    1. Re-implement convert attribute name function
    2. Investigate code of CBA tool
"""
from datetime import datetime
from .commons import sample_attribute_dict


def keys_to_lower(d):
    return {k.lower(): v for k, v in d.items()}


def convert_attribute_names(d, dict_to_reference):
    return dict((dict_to_reference[key], value) for (key, value) in d.items())


def search_pair(search_dict, field, field_val):
    fields_found = []
    for key, val in search_dict.items():
        if key == field and val == field_val:
            fields_found.append(search_dict)

        elif isinstance(val, dict):
            results = pfsHttpResult.search_pair(val, field, field_val)
            for result in results:
                fields_found.append(result)

        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    more_results = pfsHttpResult.search_pair(item, field, field_val)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found


# A simple data model that is designed to only carry the essential data of the HTTP transaction
class pfsHttpResult:
    def __init__(self, status_code: int, message: str = '', data: dict = None):
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else {}

    @staticmethod
    def search_pair(search_dict, field, field_val):
        fields_found = []
        for key, val in search_dict.items():
            if key == field and val == field_val:
                fields_found.append(search_dict)

            elif isinstance(val, dict):
                results = pfsHttpResult.search_pair(val, field, field_val)
                for result in results:
                    fields_found.append(result)

            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        more_results = pfsHttpResult.search_pair(item, field, field_val)
                        for another_result in more_results:
                            fields_found.append(another_result)

        return fields_found

    def extract_data(self, entity_type, entity_name):
        data_extract = []
        fields_found = search_pair(search_dict=self.data, field=entity_type, field_val=entity_name)
        for item in fields_found:
            new_dict = convert_attribute_names(keys_to_lower(item), sample_attribute_dict)
            data_extract.append(new_dict)
        return data_extract


class Sample:
    def __init__(self, entity_type: str, id: int, name: str, barcode: str, sequence: int, date_created: datetime,
                 date_modified: datetime, active: bool, likeby: int, followedby: int, locked: bool,
                 treatment_group: None, diet: str, bedding: str, received_alive: bool, filler_mouse: str,
                 accomodation: str, current_clinical_observation: None, anticipated_clinical_observation: None,
                 additional_notes: None, immune_status: None, customer_mouse_id: str, litter_number: None,
                 primary_id: str, primary_id_value: int, secondary_id: None, secondary_id_value: None,
                 cohort_name: None, blind_id: None, mep_id: None, nbp_group_id: None, role: None, source_pen_id: None,
                 sex: str, mouse_room_of_origin: str, section_of_origin: None, dob: datetime,
                 comments: None, dod: None, reason_for_death: None, exit_reason: None,
                 user_defined_strain_name: None, allele: str, genotype: str, coat_color: None,
                 pedigree: None, whole_mouse_fail: bool, failed_reason: None, explanation: None,
                 lot_report: str, use_for_mouse_name: bool, mouse_manifest_version: None,
                 active_status_tracker: str) -> None:
        self.entity_type = entity_type
        self.id = id
        self.name = name
        self.barcode = barcode
        self.sequence = sequence
        self.date_created = date_created
        self.date_modified = date_modified
        self.active = active
        self.likeby = likeby
        self.followedby = followedby
        self.locked = locked
        self.treatment_group = treatment_group
        self.diet = diet
        self.bedding = bedding
        self.received_alive = received_alive
        self.filler_mouse = filler_mouse
        self.accomodation = accomodation
        self.current_clinical_observation = current_clinical_observation
        self.anticipated_clinical_observation = anticipated_clinical_observation
        self.additional_notes = additional_notes
        self.immune_status = immune_status
        self.customer_mouse_id = customer_mouse_id
        self.litter_number = litter_number
        self.primary_id = primary_id
        self.primary_id_value = primary_id_value
        self.secondary_id = secondary_id
        self.secondary_id_value = secondary_id_value
        self.cohort_name = cohort_name
        self.blind_id = blind_id
        self.mep_id = mep_id
        self.nbp_group_id = nbp_group_id
        self.role = role
        self.source_pen_id = source_pen_id
        self.sex = sex
        self.mouse_room_of_origin = mouse_room_of_origin
        self.section_of_origin = section_of_origin
        self.dob = dob
        self.comments = comments
        self.dod = dod
        self.reason_for_death = reason_for_death
        self.exit_reason = exit_reason
        self.user_defined_strain_name = user_defined_strain_name
        self.allele = allele
        self.genotype = genotype
        self.coat_color = coat_color
        self.pedigree = pedigree
        self.whole_mouse_fail = whole_mouse_fail
        self.failed_reason = failed_reason
        self.explanation = explanation
        self.lot_report = lot_report
        self.use_for_mouse_name = use_for_mouse_name
        self.mouse_manifest_version = mouse_manifest_version
        self.active_status_tracker = active_status_tracker

    def get_zygosity(self) -> str:
        zygosity = '?/?'
        if self.genotype == "+/+":
            zygosity = "wild type"
        elif self.genotype == "+/-" or self.genotype == '-/+':
            zygosity = "heterozygous"
        elif self.genotype == "-/-":
            zygosity = "homozygous"
        elif self.genotype == "-/Y":
            zygosity = 'hemizygous'
        return zygosity


class Assay:

    def __init__(self):
        pass


class Experiment:

    def __init__(self):
        pass

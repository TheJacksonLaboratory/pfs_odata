import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import commons

""" simple data model that is designed to only carry the essential data of the HTTP transaction"""


class pfsHttpResult:
    def __init__(self, status_code: int, message: str = '', data: List[Dict] = None):
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else []

    @staticmethod
    def parse_json_recursively(json_object, target_key, extracted_data):
        if type(json_object) is dict and json_object:
            for key in json_object:
                if key == target_key:
                    extracted_data.append(json_object[key])
                pfsHttpResult.parse_json_recursively(json_object[key], target_key, extracted_data)
        elif type(json_object) is list and json_object:
            for item in json_object:
                pfsHttpResult.parse_json_recursively(item, target_key, extracted_data)

    '''
    TODO Sept 14th:
    1. Refactor the code snippet
    2. Create data model for sample lot
    '''
    @staticmethod
    def process():
        pass

    def convert_attributes_name(self, object_type: str) -> list[dict]:
        """
        Function to convert attribute names embedded in CORE Lims to ones CBA team needs
        :param json_objects:
        :param object_type:
        :return:
        """
        result = []
        json_object = self.data
        sample_attribute_dict = commons.sample_attribute_dict

        if object_type == "SAMPLE":
            data_out = []
            pfsHttpResult.parse_json_recursively(json_object=json_object, target_key="SAMPLE", extracted_data=data_out)
            for data in data_out:
                # Convert keys in dictionary to lower case
                temp = {k.lower(): v for k, v in data.items()}
                final_data = {(sample_attribute_dict[k] if k in sample_attribute_dict else k): v for (k, v) in
                              temp.items()}
                print(final_data)
                result.append(final_data)
            return result

        if object_type == "Sample_Lot":
            data_out = []
            pfsHttpResult.parse_json_recursively(json_object=json_object, target_key="ENTITY", extracted_data=data_out)
            for data in data_out:
                # Convert keys in dictionary to lower case
                temp = {k.lower(): v for k, v in data.items()}
                final_data = {(sample_attribute_dict[k] if k in sample_attribute_dict else k): v for (k, v) in
                              temp.items()}
                print(final_data)
                result.append(final_data)
            return result


""""Data model of API"""


class Sample:
    def __init__(self, entity_type: str, id: int, name: str, barcode: str, sequence: int, data_created: datetime,
                 date_modified: datetime, active: bool, likeby: int, followedby: int, locked: bool,
                 treatment_group: None, diet: str, bedding: str, received_alive: bool, filler_mouse: str,
                 accomodation: str, current_clinical_observation: None, anticipated_clinical_observation: None,
                 additional_notes: None, immune_status: None, customer_mouse_id: str, litter_number: None,
                 primary_id: str, primary_id_value: int, secondary_id: None, secondary_id_value: None,
                 cohort_name: None, blind_id: None, mep_id: None, nbp_group_id: None, role: None, source_pen_id: None,
                 sex: str, mouse_room_of_origin: str, section_of_origin: None, jax_mousesample_dateofbirth: datetime,
                 comments: None, date_of_death: None, reason_for_death: None, jax_mousesample_exitreason: None,
                 user_defined_strain_name: None, jax_mousesample_allele: str, genotype: str, coat_color: None,
                 jax_mousesample_pedigree: None, whole_mouse_fail: bool, fail_reason: None, explanation: None,
                 lot_report: str, use_for_mouse_name: bool, mouse_manifest_version: None,
                 active_status_tracker: str) -> None:
        self.entity_type = entity_type
        self.id = id
        self.name = name
        self.barcode = barcode
        self.sequence = sequence
        self.data_created = data_created
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
        self.jax_mousesample_dateofbirth = jax_mousesample_dateofbirth
        self.comments = comments
        self.date_of_death = date_of_death
        self.reason_for_death = reason_for_death
        self.jax_mousesample_exitreason = jax_mousesample_exitreason
        self.user_defined_strain_name = user_defined_strain_name
        self.jax_mousesample_allele = jax_mousesample_allele
        self.genotype = genotype
        self.coat_color = coat_color
        self.jax_mousesample_pedigree = jax_mousesample_pedigree
        self.whole_mouse_fail = whole_mouse_fail
        self.fail_reason = fail_reason
        self.explanation = explanation
        self.lot_report = lot_report
        self.use_for_mouse_name = use_for_mouse_name
        self.mouse_manifest_version = mouse_manifest_version
        self.active_status_tracker = active_status_tracker

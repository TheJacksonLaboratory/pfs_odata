from datetime import datetime
from typing import List, Dict, Optional
from .commons import sample_attribute_dict, sample_lot_attribute_dict, exp_assay_attribute_dict, entity_types, \
    dict_of_entity


# A simple data model that is designed to only carry the essential data of the HTTP transaction
class pfsHttpResult:
    def __init__(self, status_code: int, message: str = '', data: List[Dict] = None):
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else []

    # Function to parse json recursively to look for the value corresponding to the key entered
    @staticmethod
    def parse_json_recursively(json_object, target_key, data_to_extract):
        if type(json_object) is dict and json_object:
            for key in json_object:
                if key == target_key:
                    # In case there is a list of json data
                    if isinstance(json_object[key], list):
                        for d in json_object[key]:
                            data_to_extract.append(d)
                    else:
                        data_to_extract.append(json_object[key])
                pfsHttpResult.parse_json_recursively(json_object[key], target_key, data_to_extract)
        elif type(json_object) is list and json_object:
            for item in json_object:
                pfsHttpResult.parse_json_recursively(item, target_key, data_to_extract)

    @staticmethod
    def process(data_to_parse: list[dict], attribute_dict: dict,
                recursive: bool = False, key_word: Optional[str] = None) -> list[dict]:
        """
        Function to perform data extraction and convert the attribute names in the json
        objects to ones CBA teams need
        :param recursive:
        :type recursive:
        :param data_to_parse:
        :type data_to_parse:
        :param key_word:
        :type key_word:
        :param attribute_dict:
        :type attribute_dict:
        :return:
        :rtype:
        """
        result = []
        data_out = []
        try:
            # Nested json data case
            if recursive:
                if not key_word:
                    raise ValueError("Missing value of key to look for in the nested json")

                pfsHttpResult.parse_json_recursively(json_object=data_to_parse, target_key=entity_types[key_word],
                                                     data_to_extract=data_out)
                for data in data_out:
                    # Convert keys in dictionary to lower case
                    temp = {k.lower(): v for k, v in data.items()}
                    final_data = {(attribute_dict[k] if k in attribute_dict else k): v for (k, v) in
                                  temp.items()}
                    result.append(final_data)

                return result

            # No nested json
            else:
                for data in data_to_parse:
                    # Convert keys in dictionary to lower case
                    temp = {k.lower(): v for k, v in data.items()}
                    final_data = {(attribute_dict[k] if k in attribute_dict else k): v for (k, v) in
                                  temp.items()}
                    result.append(final_data)
                return result

        except KeyError as err:
            raise KeyError(f"No such attribute in {data_to_parse}")

    def convert_attributes_name(self, entity_type: Optional[str], recursive: bool = False) -> list[dict]:
        """
        Function to convert attribute names embedded in CORE Lims to ones CBA teams need
        :return:
        """
        entity_type = entity_type.upper().replace(" ", "_")
        if entity_type not in entity_types.keys():
            raise ValueError(f"Invalid entity type:{entity_type}")
        attribute_dict = dict_of_entity[entity_type]

        # Case when nested json data retrieved
        if recursive:
            return pfsHttpResult.process(key_word=entity_type, data_to_parse=self.data,
                                         attribute_dict=attribute_dict, recursive=True)

        # Case when non-nested json data retrieved
        else:
            return pfsHttpResult.process(key_word=entity_type, data_to_parse=self.data,
                                         attribute_dict=attribute_dict, recursive=False)


###########################################################################################################

# Data models
class Assay:
    def __init__(self):
        pass


class Experiment:
    def __init__(self):
        pass


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


class SampleLot:
    def __init__(self, entity_type: str, id: int, name: str, barcode: str, sequence: int, data_created: datetime,
                 date_modified: datetime, active: bool, likeby: int, followedby: int, locked: bool, ci_lot_num: int,
                 sample_lot_status: str, date_collected: None, date_received: datetime, collection_method: None,
                 transport_media: None, source: None, comment: None, all_lot_failed: bool, failed_reason: None,
                 fundus_required=None, fundus_comment=None) -> None:
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
        self.ci_lot_num = ci_lot_num
        self.sample_lot_status = sample_lot_status
        self.date_collected = date_collected
        self.date_received = date_received
        self.collection_method = collection_method
        self.transport_media = transport_media
        self.source = source
        self.comment = comment
        self.all_lot_failed = all_lot_failed
        self.failed_reason = failed_reason
        self.fundus_required = None if fundus_required is None else fundus_required
        self.fundus_comment = None if fundus_comment is None else fundus_comment


class Strain:

    def __init__(self, entitytypename: str, id: int, name: str, barcode: str, sequence: int, created: datetime,
                 modified: datetime, active: bool, liked_by: int, followed_by: int, locked: bool,
                 last_strain_update: datetime, privacy_label: None, owner: str, strain_status: None,
                 strain_comments: None, strain_mgi_ref_id: None, strain_komp_eap_status: None) -> None:
        self.entitytypename = entitytypename
        self.id = id
        self.name = name
        self.barcode = barcode
        self.sequence = sequence
        self.created = created
        self.modified = modified
        self.active = active
        self.liked_by = liked_by
        self.followed_by = followed_by
        self.locked = locked
        self.last_strain_update = last_strain_update
        self.privacy_label = privacy_label
        self.owner = owner
        self.strain_status = strain_status
        self.strain_comments = strain_comments


class KOMP_Strain(Strain):

    def __init__(self, entity_type_name: str, id: int, name: str, barcode: str, sequence: int, created: datetime,
                 modified: datetime, active: bool, liked_by: int, followed_by: int, locked: bool,
                 last_strain_update: datetime, privacy_label: None, owner: str, strain_status: None,
                 strain_comments: None, strain_mgi_ref_id: None, strain_komp_eap_status: None):
        super().__init__(entity_type_name, id, name, barcode, sequence, created, modified, active, liked_by,
                         followed_by, locked, last_strain_update, privacy_label, owner, strain_status, strain_comments)

        self.strain_mgi_ref_id = strain_mgi_ref_id
        self.strain_komp_eap_status = strain_komp_eap_status

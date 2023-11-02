"""
TODO Nov 2nd:
    1. Re-implement convert attribute name function
    2. Investigate code of CBA tool
"""


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


class Sample:
    def __init__(self):
        pass

    def get_zygosity(self) -> str:
        pass

from typing import List, Dict


""" simple data model that is designed to only carry the essential data of the HTTP transaction"""


class HttpResult:
    def __init__(self, status_code: int, message: str = '', data: List[Dict] = None):
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else []

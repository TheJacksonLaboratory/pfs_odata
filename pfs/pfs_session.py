import base64
import json
import logging
import sys
from datetime import datetime
from typing import Optional

import requests

from .commons import format_experiment_name, generate_filter_str, generate_orderby_str, is_date
from .models import pfsHttpResult, Sample
from .pfs_exceptions import pfsApiException


class odata_handler:
    def __init__(self):
        pass


class pfs_session:

    def __init__(self, hostname: str, tenant: str, username: str, password: str,
                 logger: logging.Logger = None):

        self.hostname = hostname
        self.tenant = tenant
        self.username = username
        self.password = password
        self.base_url = "https://{}/{}/odata/".format(hostname, tenant)
        self._logger = logger or logging.getLogger(__name__)

    @staticmethod
    def create_request(url: str, params=None, order_by: Optional[tuple] = None,
                       filter_by: Optional[str] = None, pre_filter="") -> str:
        """
        Function to form the url that will be used to make the http request.
        """
        if params is None:
            params = {}
        if order_by:
            params["$orderby"] = generate_orderby_str(order_by=order_by)
        if filter_by:
            params["$filter"] = pre_filter + generate_filter_str(filter_by)

        url = url + "&".join("{}={}".format(key, value) for key, value in params.items())
        return url

    def make_api_call(self, url: str, http_method: str, payload: dict,
                      page_size: Optional[int] = sys.maxsize) -> pfsHttpResult:
        """
        Function to make the http request

        :param page_size:
        :type page_size:
        :param url: url to make the http request
        :type url: str
        :param http_method: HTTP method, e.g. GET, PUT, POST etc
        :type http_method: str
        :param payload: Data you want to exchange when making the HTTP request
        :type payload: dict
        :return: Result of the request
        :rtype: requests.Response
        """
        userpass = self.username + ':' + self.password
        encoded_u = base64.b64encode(userpass.encode()).decode()
        headers = {
            'Accept': 'application/json',
            'prefer': f'odata.maxpagesize={page_size}',
            "Authorization": "Basic %s" % encoded_u
        }
        log_line_pre = f"method={http_method}, url={url}"
        log_line_post = ', '.join((log_line_pre, "success={}, status_code={}"))

        # Deserialize JSON output to Python object, or return failed Result on exception
        try:
            self._logger.debug(msg=log_line_pre)
            response = requests.request(http_method, url, headers=headers, data=payload)
            data_out = response.json()

        except (ValueError, json.JSONDecodeError) as e:
            self._logger.error(msg=(str(e)))
            raise pfsApiException("Bad JSON in response") from e

        is_success = 299 >= response.status_code >= 200  # 200 to 299 is OK
        log_line = log_line_post.format(is_success, response.status_code)

        # Good
        if is_success:
            self._logger.debug(msg=log_line)
            return pfsHttpResult(response.status_code, message=response.reason, data=data_out)

        self._logger.error(msg=log_line)
        raise pfsApiException()

    def authenticate(self) -> requests.Response:
        """
        Function to authenticate your account on PFS
        """
        if not self.username or not self.password:
            raise ValueError("Username and password are required")

        userpass = self.username + ':' + self.password
        encoded_u = base64.b64encode(userpass.encode()).decode()
        headers = {"Authorization": "Basic %s" % encoded_u}
        url = self.base_url + "$metadata"
        auth_result = requests.request("GET", url, headers=headers)
        return auth_result

    '''GET methods'''

    def get_experiment(self, experiment_name: str, order_by: Optional[tuple] = None,
                       filter_by: Optional[str] = None) -> pfsHttpResult:

        """
        :param experiment_name: name of the experiment/test you want to query
        :type experiment_name: str
        :param order_by: Order you want to sort your query result, please follow the format(ENTITY_ATTRIBUTE, asc / dsc)
        :type order_by: tuple

        Attention:
        Make sure that each element in one of your input "filter_by" has a one-to-one correspondence to
        other two("filter_by_values" and "operators"). e.g. filters = [JAX_ASSAY_STRAINNAME, JAX_ASSAY_DATEOFBIRTH],
        vals = ["1234567", "2000-01-01"], operators = ["=",">"]. In this example, "JAX_ASSAY_STRAINNAME" is corresponded
        to "1234567" in list "vals" and "=" in list "operators", so on and so forth.

        :param filter_by: Attributes you want to apply the filtering condition to
        :type filter_by: list
        :return: Data of input experiment(experiment_name)
        :rtype: list[dict]
        """
        url = f"{self.base_url}{experiment_name}_EXPERIMENT"
        url = self.create_request(url=url,
                                  order_by=order_by,
                                  filter_by=filter_by
                                  )
        return self.make_api_call(url=url, http_method="GET", payload={})

    def get_assay(self, experiment_name: str, order_by: Optional[tuple] = None,
                  filter_by: Optional[str] = None) -> pfsHttpResult:
        """
        Function to retrieve data of an experiment assay in Core PFS
        :param experiment_name: name of the experiment/test you want to query
        :type experiment_name: str
        :param order_by: Order you want to sort your query result, please follow the format(ENTITY_ATTRIBUTE, asc / dsc)
        :type order_by: tuple
        :param filter_by: Attributes you want to apply the filtering condition to
        :type filter_by: str
        :return: Data of input experiment(experiment_name)
        :rtype: list[dict]
        """
        pfs_assay_url = f"{self.base_url}{experiment_name}_ASSAY_DATA?"
        pfs_assay_url = self.create_request(url=pfs_assay_url,
                                            order_by=order_by,
                                            filter_by=filter_by)
        return self.make_api_call(url=pfs_assay_url, http_method="GET", payload={})

    '''
    Use this query instead:odata/MOUSE_SAMPLE?$expand=MOUSESAMPLE_STRAIN&$filter= MOUSESAMPLE_STRAIN/JAX_STRAIN_KOMP_EAP_STATUS eq 'In Progress'
    '''

    def get_meavals(self, order_by: Optional[tuple] = None,
                    filter_by: Optional[str] = None,
                    barcode: Optional[str] = None,
                    page_size: Optional[int] = sys.maxsize) -> pfsHttpResult:
        """
        Function to get all animals' measured values.
        Return a list of Sample object
        :param page_size:
        :type page_size:
        :param barcode:
        :type barcode:
        :param order_by: Order you want to sort your query result, please follow the format(ENTITY_ATTRIBUTE, asc / dsc)
        :type order_by: tuple
        :param filter_by: Attributes you want to apply the filtering condition to
        :type filter_by: str
        :return: Data in the "SAMPLE" attribute of the json data returned by the request you make
        :rtype: list[Sample]
        """

        # Construct url
        single_entity = True if barcode else False
        ENDPOINT = f"MOUSE_SAMPLE" if not single_entity else f"MOUSE_SAMPLE('{barcode}')"
        url = self.create_request(url=f"{self.base_url}{ENDPOINT}",
                                  params={},
                                  order_by=order_by,
                                  filter_by=filter_by)

        # Get data
        self._logger.info(f"Sending request to {url}")
        api_response = self.make_api_call(url=url, http_method="GET", payload={}, page_size=page_size)
        result = api_response.search_pair(api_response.data, field="EntityTypeName", field_val="MOUSE_SAMPLE")
        return result

    def get_meavals_by_proj(self, experiment_name: str, project_id: str,
                            order_by: Optional[tuple] = None):

        """
        Function to get animal measured values and animal ids, for the given procedure and filtering/ordering conditions.
        Return a list of Sample object

        :param experiment_name: name of the experiment/test you want to query, e.g CBA GLUCOSE TOLERANCE TEST, KOMP BODY WEIGHT
        :type experiment_name: str
        :param project_id: ID/Name of the experiment, normally composed by the abbreviation of the experiment and two digits
        following it, e.g GTT41 stands for Glucose Tolerance Test 41
        :type project_id: str
        :param order_by: Order you want to sort your query result, please follow the format(ENTITY_ATTRIBUTE, asc / dsc)
        :type order_by: tuple
        :return: Data in the "SAMPLE" attribute of the json data returned by the request you make
        :rtype: list[Sample]
        """
        experiment_name = format_experiment_name(experiment_name)
        ENDPOINT = f"{experiment_name}_ASSAY_DATA?"
        params = {
            "$expand": "EXPERIMENT_SAMPLE($expand=ENTITY/pfs.MOUSE_SAMPLE_LOT($expand=SAMPLE/pfs.MOUSE_SAMPLE))",
            "$filter": f"EXPERIMENT_SAMPLE/EXPERIMENT/Name eq '{project_id}'"
        }
        url = self.create_request(url=f"{self.base_url}{ENDPOINT}",
                                  params=params,
                                  order_by=order_by)
        #Get data
        result = []
        self._logger.info(f"Sending request to {url}")
        api_response = self.make_api_call(url=url, http_method="GET", payload={})
        data_extract = api_response.extract_data(entity_type="EntityTypeName", entity_name="MOUSE_SAMPLE")
        for item in data_extract:
            result.append(Sample(**item))
        return result

    def get_meavals_by_strain(self, barcode: Optional[str] = None, order_by: Optional[tuple] = None,
                              filter_by: Optional[str] = None):
        """

        :param barcode: JR Number of a string
        :type barcode: str
        :param order_by:
        :type order_by:
        :param filter_by:
        :type filter_by:
        :return:
        :rtype:
        """
        # Construct url
        single_entity = True if barcode else False
        ENDPOINT = f"JAXSTRAIN('{barcode}')?" if single_entity else "JAXSTRAIN?"
        params = {
            "$expand": "REV_MOUSESAMPLE_STRAIN"
        }
        url = self.create_request(url=f"{self.base_url}{ENDPOINT}",
                                  params=params,
                                  order_by=order_by,
                                  filter_by=filter_by)

        # Get data
        self._logger.info(f"Sending request to {url}")
        api_response = self.make_api_call(url=url, http_method="GET", payload={})
        result = api_response.search_pair(api_response.data, field="EntityTypeName", field_val="MOUSE_SAMPLE")
        return result

    # https://jacksonlabstest.platformforscience.com/DEV_KOMP/odata/KOMP_REQUEST?$expand=REV_MOUSESAMPLELOT_KOMPREQUEST($expand=SAMPLE/pfs.MOUSE_SAMPLE)
    def get_meavals_by_req(self, team: str, order_by: Optional[tuple] = None,
                           filter_by: Optional[str] = None, barcode: Optional[str] = None):
        """

        :param barcode:
        :type barcode:
        :param team:
        :type team:
        :param order_by:
        :type order_by:
        :param filter_by:
        :type filter_by:
        :return:
        :rtype:
        """

        ENDPOINT = f"{team}_REQUEST('{barcode}')?" if barcode else f"{team}_REQUEST?"
        params = {
            "$expand": "REV_MOUSESAMPLELOT_KOMPREQUEST($expand=SAMPLE/pfs.MOUSE_SAMPLE)"
        }
        url = self.create_request(url=f"{self.base_url}{ENDPOINT}",
                                  params=params,
                                  order_by=order_by,
                                  filter_by=filter_by)
        # print(url)
        result = []
        self._logger.info(f"Sending request to {url}")
        api_response = self.make_api_call(url=url, http_method="GET", payload={})
        data_extract = api_response.extract_data(entity_type="EntityTypeName", entity_name="MOUSE_SAMPLE")
        for item in data_extract:
            result.append(Sample(**item))
        return result

    def get_meavals_by_batch(self, order_by: Optional[tuple] = None,
                             filter_by: Optional[str] = None, barcode: Optional[str] = None):
        pass

    def get_sample_lot(self, experiment_name: str, order_by: Optional[tuple] = None,
                       filter_by: Optional[str] = None) -> pfsHttpResult:
        """

        Function to retrieve the data of a sample on Core PFS along with info of its assay and sample lots.

        :param experiment_name: name of the experiment/test you want to query
        :type experiment_name: str
        :param order_by: Order you want to sort your query result, please follow the format(ENTITY_ATTRIBUTE, asc / dsc)
        :type order_by: tuple
        :param filter_by: Attributes you want to apply the filtering condition to
        :type filter_by: list
        :return: Data in the "ENTITY" attribute of the json data returned by the request you make
        :rtype: list[Sample]
        """
        experiment_name = format_experiment_name(experiment_name)
        ENDPOINT = f"{experiment_name}_ASSAY_DATA?"
        params = {
            "$expand": "EXPERIMENT_SAMPLE($expand=ENTITY/pfs.MOUSE_SAMPLE_LOT)"
        }
        url = self.create_request(url=f"{self.base_url}{ENDPOINT}",
                                  params=params,
                                  order_by=order_by,
                                  filter_by=filter_by)
        self._logger.info(f"Sending request to {url}")
        return self.make_api_call(url=url, http_method="GET", payload={})

    '''POST methods'''

    def post_sample(self):
        pass

    def post_sample_lot(self):
        pass

    def update_measured_val(self):
        pass

    def update_sample_lot(self):
        pass

    def delete(self):
        pass

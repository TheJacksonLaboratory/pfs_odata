import base64
import json
import logging
from datetime import datetime
from typing import Optional

import requests

from .commons import format_experiment_name, generate_filter_str, to_odata_operator, generate_orderby_str
from .models import pfsHttpResult, Sample, SampleLot, Strain
from .pfs_exceptions import pfsApiException

"""
TODO Oct 2nd:
1. Create data model for assay, experiment and strain
2. Change some variable names in sample_attribute_dict in commons.py
"""


class pfs_session:

    def __init__(self, hostname: str, tenant: str, username: str, password: str, logger: logging.Logger = None):
        self.hostname = hostname
        self.tenant = tenant
        self.username = username
        self.password = password
        self.base_url = "https://{}/{}/odata/".format(hostname, tenant)
        self._logger = logger or logging.getLogger(__name__)

    @staticmethod
    def create_request(url: str, params=None, barcode: Optional[str] = None, order_by: Optional[tuple] = None,
                       filter_by: Optional[str] = None, pre_filter="") -> str:
        """
        Function to form the url that will be used to make the http request.
        """
        if params is None:
            params = {}
        if barcode:
            url = f"{url}('{barcode}')"
            return url
        if order_by:
            params["$orderby"] = generate_orderby_str(order_by=order_by)
        if filter_by:
            params["$filter"] = pre_filter + generate_filter_str(filter_by)

        url = url + "&".join("{}={}".format(key, value) for key, value in params.items())
        return url

    def send_request(self, url: str, http_method: str, payload: dict) -> pfsHttpResult:
        """
        Function to make the http request
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
        headers = {"Authorization": "Basic %s" % encoded_u}
        log_line_pre = f"method={http_method}, url={url}"
        log_line_post = ', '.join((log_line_pre, "success={}, status_code={}"))

        # Deserialize JSON output to Python object, or return failed Result on exception
        try:
            self._logger.debug(msg=log_line_pre)
            response = requests.request(http_method, url, headers=headers, data=payload)
            data_out = response.json()["value"]

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

        :param count:
        :type count:
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
        :param filter_by_values: Values of filtering condition you want to use
        :type filter_by_values: list
        :param operators: Logic operator you want to apply to the attributes and values
        :type operators: list
        :return: Data of input experiment(experiment_name)
        :rtype: list[dict]
        """
        url = f"{self.base_url}{experiment_name}_EXPERIMENT"
        url = self.create_request(url=url,
                                  order_by=order_by,
                                  filter_by=filter_by
                                  )
        return self.send_request(url=url, http_method="GET", payload={})

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
        return self.send_request(url=pfs_assay_url, http_method="GET", payload={})

    def get_meavals_by_expr(self, experiment_name: str, project_id: str,
                            order_by: Optional[tuple] = None) -> list[Sample]:

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
        url = f"{self.base_url}{experiment_name}_ASSAY_DATA?"
        params = {
            "$expand": "EXPERIMENT_SAMPLE($expand=ENTITY/pfs.MOUSE_SAMPLE_LOT($expand=SAMPLE/pfs.MOUSE_SAMPLE))",
            "$filter": f"EXPERIMENT_SAMPLE/EXPERIMENT/Name eq '{project_id}'"
        }
        result = []
        url = self.create_request(url=url,
                                  params=params,
                                  order_by=order_by)
        # print(url)
        self._logger.info(f"Sending request to {url}")
        response = self.send_request(url=url, http_method="GET", payload={})
        samples = response.convert_attributes_name(entity_type="SAMPLE")
        for sample in samples:
            result.append(Sample(**sample))
        return result

    '''
    Use this query instead:odata/MOUSE_SAMPLE?$expand=MOUSESAMPLE_STRAIN&$filter= MOUSESAMPLE_STRAIN/JAX_STRAIN_KOMP_EAP_STATUS eq 'In Progress'
    '''

    def get_meavals_by_strain(self, order_by: Optional[tuple] = None,
                              filter_by: Optional[str] = None) -> list[Sample]:
        """
        Function to get animal measured values and animal ids, for the given strain and filtering/ordering conditions.
        Return a list of Sample object
        :param order_by: Order you want to sort your query result, please follow the format(ENTITY_ATTRIBUTE, asc / dsc)
        :type order_by: tuple
        :param filter_by: Attributes you want to apply the filtering condition to
        :type filter_by: str
        :return: Data in the "SAMPLE" attribute of the json data returned by the request you make
        :rtype: list[Sample]
        """
        url = f"{self.base_url}MOUSE_SAMPLE?"
        result = []
        url = self.create_request(url=url,
                                  params={},
                                  order_by=order_by,
                                  filter_by=filter_by,
                                  pre_filter="MOUSESAMPLE_STRAIN/")
        self._logger.info(f"Sending request to {url}")
        response = self.send_request(url=url, http_method="GET", payload={})
        samples = response.convert_attributes_name(entity_type="MOUSE_SAMPLE", recursive=False)
        for sample in samples:
            result.append(Sample(**sample))
        return result

    def get_sample_lot(self, experiment_name: str, order_by: Optional[tuple] = None,
                       filter_by: Optional[str] = None) -> list[SampleLot]:
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
        url = f"{self.base_url}{experiment_name}_ASSAY_DATA?"
        result = []
        params = {
            "$expand": "EXPERIMENT_SAMPLE($expand=ENTITY/pfs.MOUSE_SAMPLE_LOT)"
        }
        url = self.create_request(url=url,
                                  params=params,
                                  order_by=order_by,
                                  filter_by=filter_by)
        self._logger.info(f"Sending request to {url}")
        response = self.send_request(url=url, http_method="GET", payload={})
        sample_lots = response.convert_attributes_name(entity_type="SAMPLE LOT", recursive=True)
        for lot in sample_lots:
            result.append(SampleLot(**lot))

        return result

    def get_strain(self, order_by: Optional[tuple] = None,
                   filter_by: Optional[str] = None):
        """

        :param barcode:
        :type barcode:
        :param order_by:
        :type order_by:
        :param filter_by:
        :type filter_by:
        :return:
        :rtype:
        """
        url = f"{self.base_url}JAXSTRAIN?"
        result = []
        url = self.create_request(url=url, params={}, order_by=order_by, filter_by=filter_by)
        self._logger.info(f"Sending request to {url}")
        response = self.send_request(url=url, http_method="GET", payload={})
        strains = response.convert_attributes_name(entity_type="STRAIN", recursive=False)
        for s in strains:
            result.append(Strain(**s))

        return result

    '''POST methods'''

    def post_experiment(self):
        pass

    def post_sample(self):
        pass

    def post_sample_lot(self):
        pass

    def update_experiment_vals(self):
        pass

    def update_measured_val(self):
        pass

    def update_sample_lot(self):
        pass

    def delete(self):
        pass


# --------------------------------------line-----------------------------------------
'''
mySession = pfs_session(
    hostname="jacksonlabstest.platformforscience.com",
    tenant="DEV_KOMP",
    username="tianyu.chen@jax.org",
    password="Steve19981230"
)

# sample_data = mySession.get_measured_vals(experiment_name="KOMP_BODY_WEIGHT", filter_by="JAX_ASSAY_STRAINNAME =
# TFJR0002")
#sample_data = mySession.get_meavals_by_expr(experiment_name="KOMP_BODY_WEIGHT")
#print(sample_data[0])

sample_data = mySession.get_meavals_by_strain()
print(sample_data)

sample_lot_data = mySession.get_sample_lot_data(experiment_name="CBA_GLUCOSE_TOLERANCE_TEST")
print(sample_lot_data.data["value"])
sample_lots = sample_lot_data.convert_attributes_name(entity_type="SAMPLE LOT")
# json_object = json.dumps(sample_lots[0], indent=4)
# print(json_object)
l = []
for sample_lot in sample_lots:
    l.append(SampleLot(**sample_lot))

print(l)

'''

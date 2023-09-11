import base64
from json import JSONDecodeError
from typing import Optional
from pfs_exceptions import pfsApiException
import commons
import requests
import urllib.parse
import logging
from datetime import date, time, datetime
from models import HttpResult

"""
TODO 08/31/2023

Add functionality to generate_filter_query() to handle contains operation
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
    def to_odata_operator(operator):
        try:
            return commons.operators[operator]
        except KeyError as e:
            raise KeyError()

    @staticmethod
    def generate_filter_query(filters: list[str], vals: list[any], operators: list[str]) -> str:
        """
        Function to auto-generate the odata filtering query from lists of input. e.g. filters = [
        JAX_ASSAY_STRAINNAME, JAX_ASSAY_DATEOFBIRTH], vals = ["1234567", "2000-01-01"], operators = ["=",
        ">"] Make sure that each element in one of your input lists has a one-to-one correspondence to
        other two. In the example above, "JAX_ASSAY_STRAINNAME" is corresponded to "1234567" in list
        "vals" and "=" in list "operators", so on and so forth.
        :param filters: Attributes you want to apply the filtering condition to
        :type filters: list
        :param vals: Values of filtering condition you want to use
        :type vals: list
        :param operators: Logic operator you want to apply to the attributes and values
        :type operators: list
        :return: String of OData $filter query, for more info see
                 https://learn.microsoft.com/en-us/dynamics-nav/using-filter-expressions-in-odata-uris
        :rtype: str
        """
        length = len(filters)
        if not all(len(lst) == length for lst in [filters, vals, operators]):
            raise IndexError("")
        queries = []
        for f, v, op in zip(filters, vals, operators):
            if isinstance(v, str):
                if commons.is_date(v):
                    v = datetime.strptime(v, '%Y-%m-%d').date()
                else:
                    v = f"'{v}'"
            if isinstance(v, bool):
                v = str(v)
            query = f"{f} {op} {v}"
            print(query)
            queries.append(query)

        return " and ".join(queries)

    @staticmethod
    def generate_select_query(properties: list[str]) -> str:
        """
        Function to auto-generate the odata select query from lists of input
        :param properties: Properties/attributes of an entity you want query
        :type properties: list
        :return: String of OData $select query, for more info see
                 https://learn.microsoft.com/en-us/aspnet/web-api/overview/odata-support-in-aspnet-web-api/using-select-expand-and-value
        :rtype: str
        """
        return f"{','.join(properties)}"

    @staticmethod
    def generate_order_by_query(order_by: tuple):
        """

        :param order_by:
        :type order_by:
        :return:
        :rtype:
        """
        return f"{order_by[0]} {order_by[1]}"

    @staticmethod
    def _create_request_message(url: str,
                                params=None,
                                barcode: Optional[str] = None,
                                order_by: Optional[tuple] = None,
                                select: Optional[list] = None,
                                filter_by: Optional[list] = None,  # JAX_ASSAY_STRAINNAME
                                filter_by_values: Optional[list] = None,
                                operators: Optional[list] = None  # And, Or, <, >, = etc
                                ) -> str:
        """
        Function to form the url that will be used to make the http request.
        """
        if params is None:
            params = {}
        if barcode:
            url = f"{url}('{barcode}')"
            return url
        if order_by:
            params["$orderby"] = pfs_session.generate_order_by_query(order_by=order_by)
        if filter_by:
            # params["$filter"] = f"{filter_by} {operator} '{filter_by_value}'"
            params["$filter"] = pfs_session.generate_filter_query(filters=filter_by, vals=filter_by_values,
                                                                  operators=operators)
        if select:
            # params["$select"] = f"{','.join(select)}"
            params["$select"] = pfs_session.generate_select_query(properties=select)

        url = url + "&".join("{}={}".format(key, value) for key, value in params.items())
        return url

    def _send_request(self,
                      url: str,
                      http_method: str,
                      payload: dict) -> HttpResult:
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
        log_line_post = ', '.join((log_line_pre, "success={}, status_code={}, message={}"))

        try:
            self._logger.debug(msg=log_line_pre)
            response = requests.request(http_method, url, headers=headers, data=payload)
            data_out = response.json()

        except (ValueError, JSONDecodeError) as e:
            self._logger.error(msg=(str(e)))
            raise pfsApiException("Bad JSON in response") from e

        is_success = 299 >= response.status_code >= 200  # 200 to 299 is OK
        log_line = log_line_post.format(is_success, response.status_code)

        #Good
        if is_success:
            self._logger.debug(msg=log_line)
            return HttpResult(response.status_code, message=response.reason, data=data_out)

        self._logger.error(msg=log_line)
        raise pfsApiException()

    def authenticate(self) -> HttpResult:
        """
        Function to authenticate your account on PFS
        """
        if not self.username or not self.password:
            raise ValueError("Username and password are required")

        url = self.base_url + "$metadata"
        auth_result = self._send_request(url=url, http_method="GET", payload={})
        return auth_result

    def fetch_experiment_data(self,
                              experiment_name: str,
                              order_by: Optional[tuple] = None,
                              selected_property: Optional[list] = None,
                              filter_by: Optional[list] = None,  # JAX_ASSAY_STRAINNAME
                              filter_by_values: Optional[list] = None,
                              operators: Optional[list] = None  # And, Or, <, >, = etc
                              ) -> HttpResult:

        """

        :param experiment_name: name of the experiment/test you want to query
        :type experiment_name: str
        :param order_by: Order you want to sort your query result, please follow the format(ENTITY_ATTRIBUTE, asc / dsc)
        :type order_by: tuple
        :param selected_property: Properties/attributes of an entity you want query
        :type selected_property: list

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
        pfs_expr_url = f"{self.base_url}{experiment_name}_EXPERIMENT"
        pfs_expr_url = self._create_request_message(url=pfs_expr_url,
                                                    order_by=order_by,
                                                    select=selected_property,
                                                    filter_by=filter_by,
                                                    filter_by_values=filter_by_values,
                                                    operators=operators
                                                    )
        return self._send_request(url=pfs_expr_url, http_method="GET", payload={})

    def fetch_assay_data(self,
                         experiment_name: str,
                         order_by: Optional[tuple] = None,
                         selected_property: Optional[list] = None,
                         filter_by: Optional[list] = None,  # JAX_ASSAY_STRAINNAME
                         filter_by_values: Optional[list] = None,
                         operators: Optional[list] = None  # And, Or, <, >, = etc
                         ) -> HttpResult:
        """
        Function to retrieve data of an experiment assay in Core PFS
        :param experiment_name: name of the experiment/test you want to query
        :type experiment_name: str
        :param order_by: Order you want to sort your query result, please follow the format(ENTITY_ATTRIBUTE, asc / dsc)
        :type order_by: tuple
        :param selected_property: Properties/attributes of an entity you want query
        :type selected_property: list

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
        pfs_assay_url = f"{self.base_url}{experiment_name}_ASSAY_DATA?"
        pfs_assay_url = self._create_request_message(url=pfs_assay_url,
                                                     order_by=order_by,
                                                     select=selected_property,
                                                     filter_by=filter_by,
                                                     filter_by_values=filter_by_values,
                                                     operators=operators)
        return self._send_request(url=pfs_assay_url, http_method="GET", payload={})

    def fetch_sample_data(self,
                          experiment_name: str,
                          order_by: Optional[tuple] = None,
                          selected_property: Optional[list] = None,
                          filter_by: Optional[list] = None,
                          filter_by_values: Optional[list] = None,
                          operators: Optional[list] = None
                          ) -> HttpResult:

        """
        Function to retrieve the data of a sample on Core PFS along with info of its assay and sample lots.

        :param experiment_name: name of the experiment/test you want to query
        :type experiment_name: str
        :param order_by: Order you want to sort your query result, please follow the format(ENTITY_ATTRIBUTE, asc / dsc)
        :type order_by: tuple
        :param selected_property: Properties/attributes of an entity you want query
        :type selected_property: list

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
        pfs_sample_url = f"{self.base_url}{experiment_name}_ASSAY_DATA?"
        params = {
            "$expand": "EXPERIMENT_SAMPLE($expand=ENTITY/pfs.MOUSE_SAMPLE_LOT($expand=SAMPLE/pfs.MOUSE_SAMPLE))"
        }
        pfs_sample_url = self._create_request_message(url=pfs_sample_url,
                                                      params=params,
                                                      order_by=order_by,
                                                      select=selected_property,
                                                      filter_by=filter_by,
                                                      filter_by_values=filter_by_values,
                                                      operators=operators)
        return self._send_request(url=pfs_sample_url, http_method="GET", payload={})


# --------------------------------------line-----------------------------------------

mySession = pfs_session(
    hostname="jacksonlabstest.platformforscience.com",
    tenant="DEV_KOMP",
    username="youremail",
    password="yourpassword"
)
print(mySession.base_url)
assay_data = mySession.fetch_assay_data(experiment_name="KOMP_BODY_WEIGHT",
                                        order_by=("JAX_ASSAY_DATEOFBIRTH", "asc"),
                                        selected_property=["JAX_ASSAY_STRAINNAME", "JAX_ASSAY_DATEOFBIRTH"],
                                        filter_by=["JAX_ASSAY_STRAINNAME", "JAX_ASSAY_DATEOFBIRTH"],
                                        filter_by_values=["TFJR0002", "2023-06-20"],
                                        operators=["eq", "eq"]
                                        )
print(assay_data)

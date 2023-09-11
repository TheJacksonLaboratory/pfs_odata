from pfs.pfs_session import pfs_session
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

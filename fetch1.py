from pfs.pfs_session import pfs_session
import json

"""This script is for tutorial purposes on how to pull out sample data by strain"""


# Function to print data out
def print_data(l):
    res = [i.__dict__ for i in l]
    for i in l:
        print(f"Data received is:\n {json.dumps(i.__dict__, indent=4)}")


# Create a Core PFS session
mySession = pfs_session(
    hostname="jacksonlabstest.platformforscience.com",
    tenant="DEV_KOMP",
    username="svc-limsdb@jax.org",
    password="vA&ce3(ROzAL"
)

# Authenticate using your credentials
pfs_auth_result = mySession.authenticate()
if pfs_auth_result.status_code == 200:
    print(str(pfs_auth_result.status_code) + ", OK")
else:
    print("Authentication error, please check your username and password")

# Get sample data related to a specific strain
strain_data = mySession.get_meavals_by_strain(filter_by="JAX_STRAIN_KOMP_EAP_STATUS = In Progress")
print_data(strain_data)
print(f"Number of mouse sample retrieved is {len(strain_data)}")

"""sample_lot_data = mySession.get_sample_lot(experiment_name="komp body weight")
print_data(sample_lot_data)
print(f"Number of mouse sample lots retrieved is {len(sample_lot_data)}")"""

'''strains = mySession.get_strain(filter_by="JAX_STRAIN_KOMP_EAP_STATUS = In Progress")
print_data(strains)'''
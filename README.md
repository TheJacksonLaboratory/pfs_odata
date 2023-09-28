#### Overview 

```pfs-odata``` is a Python-based SDK/API Wrapper to help pull data out of PFS / CBA.
PFS (ThermoFisher Platform For Science) is a LIMS system where the Jax
phenotyping Center stores data collected from their experiments. The main purpose of this library is to provide an easy and flexible way to interact with PFS by hiding the complexity of PFS’s embedded OData RESTful API. 

```commandline
from pfs.pfs_session import pfs_session
import json
import ast

"""This script is for tutorial purposes on how to pull out sample data by strain"""


# Function to print data out
def print_data(l):
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
strain_data = mySession.get_meavals_by_strain()
print_data(strain_data)
print(f"Number of mouse sample retrieved is {len(strain_data)}")
```
TODO 09/28/2023: 
1. Create data models for assays and experiment
2. Create a sample specimen file using the library
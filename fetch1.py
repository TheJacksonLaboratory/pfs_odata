from pfs.pfs_session import pfs_session
import pandas as pd
import datetime


def convert(date_time):
    date_format = "%Y-%m-%d"
    datetime_str = datetime.datetime.strptime(date_time, date_format)
    return datetime_str


"""This script is for tutorial purposes on how to pull out sample data by strain"""

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

# Get data from the url
result = mySession.get_meavals_by_req(team="KOMP")
#data = result.get_entity_data(key_word="SAMPLE", recursive=True)
print(f"Total number of samples get is {len(result)}")


filtered_data = []

# Say we want to filter on condition that mice's date of birth > 2023-07-31
date_to_compare = datetime.datetime(2023, 7, 31)
for d in result:
    sample_date_of_birth = convert(date_time=d["JAX_MOUSESAMPLE_DATEOFBIRTH"])
    if sample_date_of_birth > date_to_compare:
        filtered_data.append(d)

print(f"Number of samples after filtering is {len(filtered_data)}")

# Load filtered into .csv file to report
df = pd.DataFrame(filtered_data)
print(df)


#df.to_csv("Example.csv")

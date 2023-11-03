import xml.etree.ElementTree as ET
from getpass import getpass

from pfs.models import Sample
from pfs.pfs_session import pfs_session


def indent(elem, level=0):
    i = "\n" + level * "  "
    j = "\n" + (level - 1) * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


def remove_first_occurrence(s: str, c: str) -> str:
    return s.replace(c, '', 1)


# Function to get measured values of a strain
def get_specimen_data(username, password) -> list[Sample]:
    mySession = pfs_session(
        hostname="jacksonlabstest.platformforscience.com",
        tenant="DEV_KOMP",
        username=username,
        password=password
    )

    # Authenticate using your credentials
    pfs_auth_result = mySession.authenticate()
    if pfs_auth_result.status_code == 200:
        print(str(pfs_auth_result.status_code) + ", OK")
    else:
        print("Authentication error, please check your username and password")

    result = mySession.get_meavals_by_proj(experiment_name="KOMP LIGHT DARK BOX", project_id="KLDB4")
    return result


# Function to extract zygosity of a measured sample

def get_gender(gender: str) -> str:
    return "male" if gender == "M" else "female"


"""
Algorithm:
1. Iterate through list of Sample object
2. For each element in the list, create a line of record
3. Append created record to the root node

Note:
JAX_SAMPLE_EXTERNALID                                          =>           specimenID
·      JAX_MOUSESAMPLE_DATEOFBIRTH                        =>           DOB
·         JAX_MOUSESAMPLE_ALLELE                                      =>           colonyId
·         JAX_MOUSESAMPLE_GENOTYPE                              =>           zygosity
·         JAX_MOUSESAMPLE_LITTERNUMBER                     =>           litterID
·         JAX_MOUSESAMPLE_SEX                                             =>           gender
"""


def generate_xml(samples: list[Sample], filename: str):
    root = ET.Element('centreSpecimenSet',
                      {'xmlns': 'http://www.mousephenotype.org/dcc/exportlibrary/datastructure/core/specimen'})
    centerNode = ET.SubElement(root, 'centre', {'centreID': 'J'})
    specimenRecord = {
        "pipeline": 'JAX_001',
        "productionCenter": 'J',
        "phenotypingCenter": 'J',
        "project": 'JAX'
    }

    for sample in samples:
        specimenRecord["strainID"] = "MGI:3056279"
        specimenRecord["DOB"] = sample.dob
        specimenRecord["gender"] = get_gender(sample.sex)
        specimenRecord["zygosity"] = sample.get_zygosity()
        specimenRecord["litterId"] = sample.litter_number if sample.litter_number else " "

        # E.g. C57BL/6NJ-Rnf217<em1(IMPC)J>/Mmjax (JR034213), C57BL/6NJ(JR005304)
        colony_id = sample.allele
        stock = colony_id.rpartition('(')[2].partition(')')[0]
        print(stock)
        isBaseline = stock[2:] == "005304"
        if not isBaseline:
            specimenRecord["colonyID"] = remove_first_occurrence(stock, '0')
        else:
            del specimenRecord["colonyID"]

        specimenRecord["isBaseline"] = str(isBaseline).lower()

        # Create a subroot using specimenRecord
        ET.SubElement(centerNode, "mouse", specimenRecord)

    # Write content to xml file
    tree = ET.ElementTree(indent(root))
    with open(filename, "wb") as f:
        tree.write(f, xml_declaration=True, encoding='utf-8')


if __name__ == "__main__":
    username = input("Username: ")
    password = getpass()
    print("Password entered: ", password)
    specimen_data = get_specimen_data(username=username, password=password)
    generate_xml(specimen_data, filename="sample.xml")

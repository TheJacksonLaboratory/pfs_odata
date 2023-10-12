from pfs.pfs_session import pfs_session
from pfs.models import Sample
import json
from datetime import datetime
from os.path import isfile, join, basename
import glob
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import xml.dom.minidom
from lxml import etree, builder


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


# Function to remove namespace in the xml data
def remove_namespace(doc, namespace):
    ns = u'{%s}' % namespace
    nsl = len(ns)
    for elem in doc.getiterator():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]


def get_stock_number(s) -> str:
    pass


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

    # Get sample data related to a specific strain
    result = mySession.get_meavals_by_strain(filter_by="JAX_STRAIN_KOMP_EAP_STATUS = In Progress")
    return result


# Function to extract zygosity of a measured sample
def get_zygosity(sample) -> str:
    if not sample:
        return ''
    zygosity = '?/?'
    if sample.genotype == "+/+":
        zygosity = "wild type"
    elif sample.genotype == "+/-" or sample.genotype == '-/+':
        zygosity = "heterozygous"
    elif sample.genotype == "-/-":
        zygosity = "homozygous"
    elif sample.genotype == "-/Y":
        zygosity = 'hemizygous'
    else:
        print("Invalid genotype value detected")

    return zygosity


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
        specimenRecord["specimenID"] = sample.specimen_id
        specimenRecord["DOB"] = sample.date_of_birth
        specimenRecord["gender"] = sample.sex
        specimenRecord["zygosity"] = get_zygosity(sample)
        specimenRecord["litterId"] = "litterId"
        # sample.litter_number

        # Create a subroot using specimenRecord
        ET.SubElement(centerNode, "mouse", specimenRecord)
        # centerNode.append(paramNode)

    #
    # indent the xml
    """xml_p = xml.dom.minidom.parseString(ET.tostring(root))
    tree = ET.ElementTree(ET.fromstring(xml_p.toprettyxml()))"""
    # tree = ET.ElementTree(indent(root))

    tree = ET.ElementTree(indent(root))
    with open(filename, "wb") as f:
        tree.write(f, xml_declaration=True, encoding='utf-8')


if __name__ == "__main__":
    pfs_username = "svc-limsdb@jax.org"
    pfs_password = "vA&ce3(ROzAL"

    specimen_data = get_specimen_data(username=pfs_username, password=pfs_password)
    generate_xml(specimen_data, filename="sample.xml")

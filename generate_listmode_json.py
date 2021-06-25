import json
import pydicom
import argparse
from datetime import datetime

pet_json_template = {
    #
    # general information
    #
    "Manufacturer": "Siemens",
    "ManufacturersModelName": "Biograph_mMR",
    "InstitutionName": "Monash University",
    "InstitutionalDepartmentName": "Biomedical Imaging",
    "BodyPart": "brain",
    "Unit": "Bq/ml",
    "TracerName": "FDG",
    "TracerRadLex": "RID11701",
    "TracerSNOMED": "http://purl.bioontology.org/ontology/SNOMEDCT/764660008",
    "TracerRadionuclide": "F18",
    "TracerMolecularWeight": 181.26,
    "TracerMolecularWeightUnit": "g/mol",
    "PharmaceuticalDoseUnit": "Bq/g",
    "PharmaceuticalDoseRegimen": "IV infusion",
    "PharmaceuticalDoseTime": [0, 90],
    "PharmaceuticalDoseTimeUnit": "s",
    #
    # radiochem
    #
    # "InjectedRadioactivity": None, # unknown
    "InjectedRadioactivityUnit": "MBq",
    "InjectedMassPerWeightUnit": "MBq/mL",
    "SpecificRadioactivityUnit": "MBq",
    "ModeOfAdministration": "infusion",
    "InfusionSpeed": 0.01,
    "InfusionSpeedUnit": "mL/s",
    "InjectedVolumeUnit": "mL",
    #
    # time section
    #
    # "ScanDate": None, # equal to the acquisitionDate yy:mm:dd
    # "TimeZero": None, # InjectionTime
    # "ScanStart": None, # acquisition Time to hh:mm:ss
    # "InjectionStart": None,
    # "InjectionEnd": None,
    "FrameTimesStartUnit": "s",
    "FrameDuration": 16,
    "FrameDurationUnit": "s",
    # "FrameTimesStart": None,
    #
    # recon section
    #
    # "AcquisitionMode": "list mode",
    # "ImageDecayCorrected": True,
    # "DiameterFOV": 258,
    # "DiameterFOVUnit": "mm",
    # "ImageOrientation": "3D",
    # "ReconMatrixSize": 344,
    # "ReconMethodName": "3D Iterative",
    # "ReconMethodParameterLabels": ["subsets", "iterations", "zoom"],
    # "ReconMethodParameterUnit": ["none", "none", "none"],
    # "ReconMethodParameterValues": [21, 3, 1],
    # "ReconMethodImplementationVersion": "Syngo VB20 P",
    # "ReconFilterType": "Gaussian",
    # "ReconFilterSize": 4,
    # "AttenuationCorrection": "DIXON Brain HiRes",
    # "ScatterFraction": 44.32,
    # "DecayCorrectionFactor": 1.07238,
    #
    # blood section
    #
    "PlasmaAvail": True,
    # "PlasmaFreeFraction", None,
    "PlasmaFreeFractionMethod": "Counts per minute(CPM)",
    "MetaboliteAvail": False,
    "MetaboliteRecoveryCorrectionApplied": False,
    "ContinuousBloodAvail": False,
    "ContinuousBloodDispersionCorrected": False,
    "DiscreteBloodAvail": False,
    "DiscreteBloodDensity": "g/dl",
}

ignore_list = []

allow_list = [
    "Specific Character Set",
    "Implementation Version Name",
    "Image Type",
    "Instance Creation Date",
    "Instance Creation Time",
    "Study Date",
    "Series Date",
    "Acquisition Date",
    "Study Time",
    "Series Time",
    "Acquisition Time",
    "Modality",
    "Manufacturer",
    "Institution Name",
    "Manufacturer Model Name",
    "Software Versions",
    "Protocol Name",
    "Patient Position",
    "Image Comments",
    "CSA Data Type",
    "CSA Data Version",
    "CSA Image Header Type",
    "CSA Image Header Version",
    "CSA Series Header Type",
    "CSA Series Header Version",
    "Series Workflow Status",
]


def add_time_info(dicom_header, injection_time):
    return {
        "ScanDate": f"{dicom_header['AcquisitionDate'][:4]}:{dicom_header['AcquisitionDate'][4:6]}:{dicom_header['AcquisitionDate'][6:]}",
        "TimeZero": injection_time,
        "ScanStart": (
            datetime.strptime(dicom_header["AcquisitionTime"][:6], "%H%M%S")
            - datetime.strptime(injection_time, "%H:%M:%S")
        ).total_seconds(),
        "InjectionStart": 0,
    }


def main(args):
    header_info = {}

    # read the dicom file
    img = pydicom.read_file(args.dicom_file)

    for each in img.iterall():
        key = None

        if type(each.name) == list:
            if each.name[0] in allow_list:
                key = each.name[0]
        else:
            if each.name in allow_list:
                key = each.name

        value = (
            list(each.value)
            if type(each.value) == pydicom.multival.MultiValue
            else each.value
        )

        if key:
            header_info[key.replace(" ", "")] = value

    # add the pet-mr information
    header_info.update(pet_json_template)

    # add time information
    header_info.update(add_time_info(header_info, args.injection_time))

    # save to json
    with open(args.dicom_file.replace(".dcm", ".json"), "w") as outfile:
        json.dump(header_info, outfile, indent=3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dicom_file", help="dicom file to extract header information")
    parser.add_argument(
        "injection_time", type=str, help="injection time in the format of hh:mm:ss"
    )
    args = parser.parse_args()

    main(args)
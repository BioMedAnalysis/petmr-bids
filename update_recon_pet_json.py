import json
import pydicom
import argparse
from datetime import datetime
import glob
import os

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
    "AcquisitionMode": "list mode",
    "ImageDecayCorrected": True,
    "ReconMethodName": "PSF-OP-OSEM2i21s",
    "ReconMethodParameterLabels": ["subsets", "iterations", "zoom"],
    "ReconMethodParameterUnit": ["subset", "subiteration", "none"],
    "ReconMethodParameterValues": [21, 3, 1],
    "ReconMethodImplementationVersion": "Syngo VB20 P",
    "ReconFilterType": "Gaussian",
    # "ReconMatrixSize": 344,
    # "ReconFilterSize": 4,
    "AttenuationCorrection": "DIXON Brain HiRes",
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


allow_list = [
    "Acquisition Date",
    "Acquisition Time",
    "Series Time",
    "Modality",
    "Manufacturer",
    "Institution Name",
    "Slice Thickness",
    "Software Versions",
    "Patient Position",
    "Image Position (Patient)",
    "Image Orientation (Patient)",
    "Radiopharmaceutical",
    "Radiopharmaceutical Start Time",
    "Radionuclide Half Life",
    "Radionuclide Positron Fraction",
    "Code Value",
    "Number of Slices",
    "Number of Time Slices",
    "Counts Source",
    "Randoms Correction Method",
    "Attenuation Correction Method",
    "Decay Correction",
    "Reconstruction Method",
    "Scatter Correction Method",
    "Axial Acceptance",
    "Axial Mash",
    "Decay Factor",
    "Dose Calibration Factor",
    "Scatter Fraction Factor",
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

    with open(args.json_file) as f:
        json_data = json.load(f)

    header_info = {}

    # read the dicom file
    files = glob.glob(args.dicom_dir + "/*.dcm")
    files.sort(key=os.path.getmtime)
    img = pydicom.read_file(files[0])

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
    json_data.update(header_info)

    # add time information
    json_data.update(add_time_info(header_info, args.injection_time))

    # save to json
    with open("new_" + args.json_file, "w") as outfile:
        json.dump(json_data, outfile, indent=3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="the generated json file by heudiconv")
    parser.add_argument(
        "dicom_dir", type=str, help="director of raw pet reconstructed dicom filesy"
    )
    parser.add_argument(
        "injection_time", type=str, help="injection time in the format of hh:mm:ss"
    )
    args = parser.parse_args()

    main(args)

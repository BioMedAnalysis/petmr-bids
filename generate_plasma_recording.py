import json
import argparse

plasma_blood_discrite_json_template = {
    "SampleTime": {
        "Description": "Time of sampling blood wrt to TimeZero",
        "Units": "s",
    },
    "MeasurementTime": {
        "Description": "Time of measuring counts wrt to TimeZero",
        "Units": "s",
    },
    "CPM": {"Description": "Counts Per Minutes measurement", "Units": "unitless"},
    "TC": {"Description": "Total counts measurement", "Units": "unitless"},
}

blood_template = {
    "PlasmaAvail": True,
    "MetaboliteAvail": False,
    "MetaboliteRecoveryCorrectionApplied": False,
    "ContinuousBloodAvail": False,
    "ContinuousBloodDispersionCorrected": False,
    "DiscreteBloodAvail": True,
}


naming_suffix_blood = "_blood.json"
naming_suffix_json = "_recording-blood_discrete.json"
# naming_suffix_tsv = "_recording-blood_discrete.tsv"


def save_json_file(subject_prefix):
    with open(subject_prefix + naming_suffix_json, "w") as json_file:
        json.dump(plasma_blood_discrite_json_template, json_file, indent=3)


def save_blood_json(subject_prefix):
    with open(subject_prefix + naming_suffix_blood, "w") as json_file:
        json.dump(blood_template, json_file, indent=3)


# def save_tsv(subject_prefix, injection_start, tsv_raw):
#      with open(subject_prefix + naming_suffix_tsv, 'w') as tsv_file:
#          pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "injection_start", help="The start time of injection in format hh:mm:ss"
    # )
    parser.add_argument("subject", help="the subject information as prefix")
    # parser.add_argument("tsv_raw", help="the raw measurments in tsv format")
    args = parser.parse_args()

    save_json_file(args.subject)
    save_blood_json(args.subject)
    # save_tsv(args.injection_start, args.tsv_raw)

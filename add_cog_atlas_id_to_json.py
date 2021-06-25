import glob
import json

task_url = 'https://cognitiveatlas.org/task/id/trm_4c898f8f297ac/' # flashing checkerboard
rest_url = 'https://cognitiveatlas.org/task/id/trm_54e69c642d89b/'  # rest eyes closed


def get_files(pattern):
    return glob.glob(pattern)

def add_field_to_json(json_file, new_key, new_value):
    with open(json_file) as _file:
        json_data = json.load(_file)

    json_data[new_key] = new_value

    with open(json_file, 'w') as _file:
        json.dump(json_data, _file, indent=4)


def main():
    task_files = get_files("*checker*.json")
    rest_files = get_files("*rest*.json")

    for each in task_files:
        add_field_to_json(each, 'CogAtlasID', task_url)

    for each in rest_files:
        add_field_to_json(each, 'CogAtlasID', rest_url)


if __name__ == '__main__':
    main()

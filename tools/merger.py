import json
import os
import glob
import shutil
from collections import defaultdict

json_folder = './template/zh_TW'
extensions_folder = './template/zh_TW/extensions'
merged_file = './localizations/zh_TW.json'
report_file = './tools/merge_report.txt'


def merge_json_files():
    # Get all JSON files in the folder
    json_files = glob.glob(os.path.join(json_folder, '*.json'))
    if os.path.exists(extensions_folder):
        json_files += glob.glob(os.path.join(extensions_folder, '*.json'))
    # print(json_files)
    # Put StableDiffusion.json as the first element in the list
    stable_diffusion_file = './template/zh_TW\\StableDiffusion.json'
    if stable_diffusion_file in json_files:
        json_files.remove(stable_diffusion_file)
        json_files.insert(0, stable_diffusion_file)
    print(json_files)
    # Merge all JSON files
    merged = defaultdict(lambda: defaultdict(str))
    duplicate_keys = defaultdict(list)
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key in data.keys():
                if key in merged and isinstance(merged[key], dict) and isinstance(data[key], dict):
                    # Key already exists, recursively merge subkeys
                    merged[key] = merge_dict(
                        merged[key], data[key], duplicate_keys, file)
                elif key in merged:
                    # Key already exists, add to list of duplicate keys
                    duplicate_keys[key].append(file)
                else:
                    merged[key] = data[key]

    # Write merged JSON file
    with open(merged_file, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=4)

    # Write report file
    with open(report_file, 'w', encoding='utf-8') as f:
        if len(duplicate_keys) > 0:
            f.write('Duplicate keys found in these files: \n')
            for key, files in duplicate_keys.items():
                f.write(f'\n"{key}"\n')
                for file in files:
                    f.write(f'"{file}" - ')
                    # Get the value for the key in the file
                    with open(file, 'r', encoding='utf-8') as f2:
                        data = json.load(f2)
                        value = data.get(key)
                    # Write the value for the key in the file
                    f.write(f'"{value}".\n')
        else:
            f.write('Duplicate keys not found.')


def merge_dict(dict1, dict2, duplicate_keys, file):
    # Recursively merge dictionaries
    for key in dict2.keys():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            # Key already exists, recursively merge subkeys
            dict1[key] = merge_dict(
                dict1[key], dict2[key], duplicate_keys, file)
        elif key in dict1:
            # Key already exists, add to list of duplicate keys
            duplicate_keys[key].append(file)
        else:
            dict1[key] = dict2[key]
    return dict1


if __name__ == '__main__':
    merge_json_files()

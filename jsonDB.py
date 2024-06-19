import json
import os


def read_db(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def write_db(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)


def update_db(filename, key, value):
    data = read_db(filename)
    if isinstance(data, dict) and isinstance(value, dict):
        data[key] = value
    else:
        print("Error: Existing data is not a dictionary.")
    write_db(filename, data)


def delete_from_db(filename, key):
    data = read_db(filename)
    if key in data:
        del data[key]
        write_db(filename, data)

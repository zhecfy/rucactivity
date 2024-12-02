import os
import json

def save_json(json_object, file_path):
    file_path = os.path.abspath(file_path)
    # print(f"saving to file: {file_path}")

    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    file = open(file_path, "w", encoding='utf-8')
    assert file is not None
    json.dump(json_object, file, ensure_ascii=False, indent=4)
    file.close()
    return

def load_json(file_path):
    file_path = os.path.abspath(file_path)
    # print(f"loading file: {file_path}")

    if not os.path.exists(file_path):
        return None
    
    file = open(file_path, "r", encoding='utf-8')
    assert file is not None
    json_object = json.load(file)
    file.close()
    return json_object
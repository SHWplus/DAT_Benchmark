import os
import json

def get_dir_info(path):
    dir_dict = {}
    for root, dirs, files in os.walk(path):
        if not dirs:
            dir_dict[root] = []
        if root in dir_dict:
            dir_dict[root].append(len(files))
    return dir_dict

if __name__ == '__main__':
    path = './droneVideos'
    dir_dict = get_dir_info(path)
    print(dir_dict)
    # create json
    json_data = {}
    for k, v in dir_dict.items():
        parent_dir = os.path.basename(os.path.dirname(k))
        child_dir = os.path.basename(k)
        if parent_dir not in json_data:
            json_data[parent_dir] = {}
        json_data[parent_dir][child_dir] = sum(v) - 1

    with open('dir_info.json', 'w') as f:
        json.dump(json_data, f, indent=4)


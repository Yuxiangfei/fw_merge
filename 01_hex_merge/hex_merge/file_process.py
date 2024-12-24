import json




def get_content_list(file_path, content_list):
    with open(file_path, 'r') as file:
        for line in file.readlines():
            content_list.append(list(line))
        file.close()
    #print(content_list)



def write_by_list(file_path, content_list):
    line_str = ""
    for list in content_list:
        line_str += ''.join(list)
    #print(line_str)

    if len(line_str) != 0:
        with open(file_path, 'w') as file:
            file.write(line_str)
            file.close()


def get_json_content(file_path):
    with open(file_path, 'r') as file:
        json_content = json.load(file)
        file.close()
    #print(json_content)
    return json_content




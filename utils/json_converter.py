import json
import os

def create_node(name, parent, node=True):
    node_dict = dict()
    node_dict['name'] = name
    node_dict['parent'] = parent
    if node is True:
        node_dict['children'] = list()
    return node_dict

data = list()
data.append(create_node('file code', 'null'))

d = '[{\"name\": "file code", "parent": "null", "children": []}]'

with open('jsonTest.txt', mode='w') as outfile:
    json.dump(data, outfile)


def convert_data_to_json(numberOfFiles=1000,
                         targetFolder=os.path.join('output', 'regex_xml'),
                         jsonOutFileName='regex_json_file_dep'):
    data = dict()
    data['content'] = dict()
    fileCounter = 1
    if os.path.isdir(targetFolder):
        for file in os.listdir(targetFolder):
            print('Processing: {0}'.format(file))
            if fileCounter <= numberOfFiles:
                with open(os.path.join(targetFolder, file), mode='r') as targetFile:
                    readData = targetFile.read()
                    data['content'][file[:-4]] = readData
                fileCounter += 1
            else:
                break
        print('Writing json File')
        with open(os.path.join('output', jsonOutFileName), mode='w') as outputFile:
            json.dump(data, outputFile)


# convert_data_to_json()

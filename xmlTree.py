import re
import xml.etree.ElementTree as ET
import os
import csv
from utils.util_functions import strip_tags, init_section_structure
from project_config import parser
# # create the file structure
# data = ET.Element('data')
# section1 = ET.SubElement(data, 'section')
# section2 = ET.SubElement(data, 'section')
# section1.set('name', 'Section1')
# section2.set('name', 'Section2')
# for _ in range(10):
#     sentence = ET.SubElement(section1, 'S')
#     sentence.text = 'Test Text'
#
# # create a new XML file with the results
# mydata = ET.tostring(data)
# myfile = open("items2.xml", "wb")
# myfile.write(mydata)


def createXmlDocument(text, fileName, path=os.path.join('output', 'xml')):
    if not os.path.isdir(path):  # Checks if directory exists
        os.mkdir(path)
    section = None
    data = ET.Element('data')
    for sent in text:
        if sent.find('<P>') is not -1:  # checks if there is any section tags in the current sentence
            sent = sent.strip().split('\n')  # Removes the \n and splits the string by <P>
            section_exists = False
            for elem in data:
                if len(elem.attrib) != 0 and elem.attrib['name'].lower() == re.sub('^[0-9]+\s?', '', sent[sent.index('<P>') + 1]).lower():  # Checks if section exists in the xml
                    section_exists = True
                    section = elem  # updates section variable to the element found so the sentences will be added to the section exists
                    break
            if section_exists:
                continue
            section = ET.SubElement(data, 'section')  # Creates new xml Section tag
            # section.set('name', sent[sent.index('<P>') + 1])  # finds the name of the section to be put in the xml tag
            section.set('name', re.sub('[0-9]+\s?', '', sent[sent.index('<P>') + 1]))
        elif len(data.attrib) == 0 and section is None:
            sentence = ET.SubElement(data, 'S')
            sentence.text = sent
        else:
            sentence = ET.SubElement(section, 'S')
            sentence.text = sent
    with open(path + fileName + ".xml", "wb") as xmlWriter:
        newData = ET.tostring(data)
        newData = re.sub(b'[\x00-\x08|\x0B|\x0C|\x0E-\x1F|\x7F-\x84|\x86-\x9F]', b'', newData)
        # for code in removeCodes:
        #     newData = newData.replace(code, b'')
        xmlWriter.write(newData)


def readXmlDocument(fileName, path=os.path.join('output', 'xml')):
    fileDict = dict()
    fileDict['other'] = ''
    if not os.path.isdir(path):
        print("Cannot read files, xml folder does not exists. Exiting program")
        exit(1)
    # tree = ET.parse(path + fileName)  # .xml File string name
    tree = ET.parse(os.path.join(path, fileName))  # .xml File string name
    root = tree.getroot()
    for elem in root:
        if len(elem.attrib) is 0:
            fileDict['other'] += elem.text
        else:
            fileDict[elem.attrib['name']] = ''
        for subelem in elem:
            # print(elem.text)
            fileDict[elem.attrib['name']] += subelem.text
    return fileDict


def calculateStats():
    xmlDataStats = dict()
    for filename in os.listdir("output/xml"):
        if filename != 'data_processed.csv':
            try:
                ans = readXmlDocument(filename)
                xmlDataStats[int(filename.replace('.txt.xml', ''))] = len(ans) - 1  # remove 1 element for base other element
            except Exception:
                print("Exception parsing file: " + filename)
                xmlDataStats[int(filename.replace('.txt.xml', ''))] = -1
    # Calculate AVG
    avg_sum = 0
    for file in xmlDataStats.keys():
        avg_sum += xmlDataStats[file]
    avg_sections = avg_sum / float(len(xmlDataStats))
    print("In average the pre-process finds {:0.3f} sections per file.".format(avg_sections))
    # Write data to local csv file
    with open('output/xml/data_processed.csv', mode='w') as dataProc:
        dataProcWriter = csv.writer(dataProc, delimiter=',')
        dataProcWriter.writerow(['ID', 'Counter'])
        for res in xmlDataStats:
            dataProcWriter.writerow([res, xmlDataStats[res]])


def createXmlDocument_v2(text, fileName, path=parser.get('xmlTree', 'createXmlDocument_v2_path')):
    sections_type = init_section_structure()
    if not os.path.isdir('output'):
        os.mkdir('output')
    if not os.path.isdir(path):  # Checks if directory exists
        os.mkdir(path)
    section = None
    data = ET.Element('data')
    for sent in text:
        if sent.startswith('<H-'):
            section_exists = False
            sent_strip, section_id = strip_tags(sent, 'H')
            for elem in data:
                if len(elem.attrib) != 0 and elem.attrib['name'] == sections_type[section_id]:
                    section_exists = True
                    section = elem  # updates section variable to the element found so the sentences will be added to the section exists
                    break
            if section_exists:
                continue
            section = ET.SubElement(data, 'section')

            section.set('name', sections_type[section_id])
            section.text = sent_strip
        if sent.startswith('<S>'):
            if section is None:
                sent = strip_tags(sent, 'S')
                sentence = ET.SubElement(data, 'S')
                sentence.text = sent
            else:
                sent = strip_tags(sent, 'S')
                sentence = ET.SubElement(section, 'S')
                sentence.text = sent
        if sent.startswith('<OneItem>'):
            if section is None:
                sent = strip_tags(sent, 'OneItem')
                sentence = ET.SubElement(data, 'OneItem')
                sentence.text = sent
            else:
                sent = strip_tags(sent, 'OneItem')
                sentence = ET.SubElement(section, 'OneItem')
                sentence.text = sent
    with open(path + fileName + ".xml", "wb") as xmlWriter:
        newData = ET.tostring(data)
        newData = re.sub(b'[\x00-\x08|\x0B|\x0C|\x0E-\x1F|\x7F-\x84|\x86-\x9F]', b'', newData)
        xmlWriter.write(newData)
    return path + fileName + ".xml"


def read_xml_file(filename_path, filename, target_dir=parser.get('xmlTree', 'read_xml_file_target_dir')):
    stats_counter = {'name': filename,
                     'words': 0,
                     'sentences': 0,
                     'sections': 0,
                     'wordsPerSection': 0}

    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)
    tree = ET.parse(filename_path)
    root = tree.getroot()

    with open(os.path.join(target_dir, filename), mode='w') as txtXml:
        for elem in root:
            if elem.tag == 'S':
                txtXml.write(elem.text + '\n')
                print(elem.text)
                # Stat
                stats_counter['sentences'] += 1
                stats_counter['words'] += len(elem.text.strip().split())
            elif elem.tag == 'section':
                txtXml.write(elem.attrib['name'] + '\n')
                print(elem.attrib['name'])
                # Stat
                stats_counter['sections'] += 1
                stats_counter['words'] += len(elem.attrib['name'].strip().split())
            elif elem.tag == 'OneItem':
                txtXml.write(elem.text + '\n')
                print(elem.text)
                stats_counter['words'] += len(elem.text.strip().split())
            for subelem in elem:
                txtXml.write(subelem.text + '\n')
                print(subelem.text)
                stats_counter['words'] += len(subelem.text.strip().split())
                stats_counter['wordsPerSection'] += len(subelem.text.strip().split())

    # Write to stat file
    with open('data_set_statistics.csv', mode='a') as statFile:
        fieldNames = list(stats_counter.keys())
        writer = csv.DictWriter(statFile, fieldnames=fieldNames)
        writer.writerow(stats_counter)


def temp_create_text_xml_files(source_dir=os.path.join('output', 'xml')):
    for filename in os.listdir(source_dir):
        read_xml_file(os.path.join(source_dir, filename), filename[:-4])


# temp_create_text_xml_files()

# region Discourse xml functions
# ==== Xml Functions ====
def read_xml_file_discourse(filename, target_dir=os.path.join('output', 'xml')):
    parsed_dict = dict()
    current_tag = 'non_section'  # base tag
    last_index = -1
    sent = False
    parsed_dict[current_tag] = list()

    tree = ET.parse(os.path.join(target_dir, filename))
    root = tree.getroot()
    for elem in root:
        if elem.tag == 'S':
            # parsed_dict[current_tag].append(elem.text) previous_version
            if len(parsed_dict[current_tag]) == 0:
                sent = True
                parsed_dict[current_tag].append(elem.text)
                last_index += 1
            elif not elem.text.endswith('.') and sent is True:
                parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + elem.text
            elif not elem.text.endswith('.') and sent is False:
                sent = True
                last_index += 1
                parsed_dict[current_tag].append(elem.text + ' ')
            elif sent is True:
                sent = False
                parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + elem.text
            else:
                sent = False
                last_index += 1
                parsed_dict[current_tag].append(elem.text)
            print(elem.text)
        elif elem.tag == 'section':
            current_tag = elem.attrib['name']
            last_index = -1
            parsed_dict[current_tag] = list()
            print(elem.attrib['name'])
        elif elem.tag == 'OneItem':
            # parsed_dict[current_tag].append(elem.text)
            if len(parsed_dict[current_tag]) == 0:
                sent = True
                parsed_dict[current_tag].append(elem.text + ' ')
                last_index += 1
            # elif not elem.text.endswith('.'):
            #     parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + elem.text
            elif elem.text.endswith('.') and sent is False:
                last_index += 1
                parsed_dict[current_tag].append(elem.text + ' ')
            else:
                sent = True
                last_index += 1
                parsed_dict[current_tag].append(elem.text + ' ')
            print(elem.text)
        for subelem in elem:
            # parsed_dict[current_tag].append(subelem.text)
            if subelem.tag == 'S':
                # parsed_dict[current_tag].append(elem.text) previous_version
                if len(parsed_dict[current_tag]) == 0:
                    sent = True
                    parsed_dict[current_tag].append(subelem.text)
                    last_index += 1
                elif not subelem.text.endswith('.') and sent is True:
                    parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + subelem.text
                elif not subelem.text.endswith('.') and sent is False:
                    sent = True
                    last_index += 1
                    parsed_dict[current_tag].append(subelem.text + ' ')
                elif sent is True:
                    sent = False
                    parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + subelem.text
                else:
                    sent = False
                    last_index += 1
                    parsed_dict[current_tag].append(subelem.text)
                print(subelem.text)
            elif subelem.tag == 'OneItem':
                # parsed_dict[current_tag].append(elem.text)
                if len(parsed_dict[current_tag]) == 0:
                    sent = True
                    parsed_dict[current_tag].append(subelem.text + ' ')
                    last_index += 1
                # elif not elem.text.endswith('.'):
                #     parsed_dict[current_tag][last_index] = parsed_dict[current_tag][last_index] + elem.text
                elif subelem.text.endswith('.') and sent is False:
                    last_index += 1
                    parsed_dict[current_tag].append(subelem.text + ' ')
                else:
                    sent = True
                    last_index += 1
                    parsed_dict[current_tag].append(subelem.text + ' ')
            print(subelem.text)
    return parsed_dict


def create_temp_file(xml_parse_result, file_name, base_dir=os.path.join('output', 'xmlParse')):
    sub_path = os.path.join(base_dir, file_name[:-8])
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    elif not os.path.exists(sub_path):
        os.mkdir(sub_path)
    for section in xml_parse_result.keys():
        with open(os.path.join(sub_path, file_name[:-8] + '_' + section.replace(' ', '_') + '.txt'), mode='w') as tmp_files:
            for item in xml_parse_result[section]:
                tmp_files.write(item + '\n')


def parse_xml_to_sub_file(file_name):  # Input example: '17.txt.xml'
    parsed_xml = read_xml_file_discourse(file_name)
    # text = remove_long_sentences(parsed_xml)
    # create_temp_file(text.split('\n'), file_name)
    create_temp_file(parsed_xml, file_name)


def create_section_files(base_dir='output'):
    for sectioned_xml in os.listdir(os.path.join(base_dir, 'xml')):
        parse_xml_to_sub_file(sectioned_xml)
# endregion

# create_section_files()

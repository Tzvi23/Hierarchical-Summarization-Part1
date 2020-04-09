"""
!!! This file is not used in the project anymore
"""
# TODO check if can be deleted
import xml.etree.ElementTree as ET
import os
import copy
import pickle




def get_jaccard_sim(str1, str2):
    a = set(str1.split())
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))

def init_sectionNames_dict(mode='list'):
    """ NOT USED """
    corpusDict = dict()
    sections_types = ['chairmans statement', 'chief executive officer ceo review', 'chief executive officer ceo report',
                      'governance statement',
                      'remuneration report',
                      'business review', 'financial review', 'operating review', 'highlights', 'auditors report',
                      'risk management', 'chairmans governance introduction',
                      'Corporate Social Responsibility CSR disclosures']
    for section in sections_types:
        if mode == 'list':
            corpusDict[section.lower()] = list()
        if mode == 'float':
            corpusDict[section.lower()] = float(0)
    return corpusDict


def createCorpusBySectionName(dir_path='output/xml/'):
    sectionNames = list()
    file_corpus = dict()
    corpus = dict()
    for filename in os.listdir(dir_path):
        print('Processing: {0}'.format(filename))
        if filename.endswith('.txt.xml'):
            corpus.clear()
            tree = ET.parse(dir_path + filename)
            root = tree.getroot()
            for elem in root:
                if elem.attrib:
                    if elem.attrib['name'].lower() not in corpus:
                        corpus[elem.attrib['name'].lower()] = list()
                    for sub_element in elem:
                        corpus[elem.attrib['name'].lower()].append(sub_element.text)
            file_corpus[int(filename[:-8])] = copy.deepcopy(corpus)
        for sectionName in corpus.keys():
            sectionNames.append(sectionName)
    return file_corpus, set(sectionNames)


def loadCorpus(file, dir_path='saved_data'):
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
        files_pickle, sections_pickle = createCorpusBySectionName()
        with open(dir_path + '/' + file, 'wb') as saveFile:
            print('Saving data to {0} ...'.format(dir_path + '/' + file))
            pickle.dump([files_pickle, sections_pickle], saveFile)
            print('Created {0} and saved'.format(file))
    else:
        if os.path.isfile(dir_path + '/' + file):
            with open(dir_path + '/' + file, 'rb') as saveFile:
                print('Loading {0} ...'.format(file))
                files_pickle, sections_pickle = pickle.load(saveFile)
        else:
            files_pickle, sections_pickle = createCorpusBySectionName()
            with open(dir_path + '/' + file, 'wb') as saveFile:
                print('Created {0} and saved'.format(file))
                pickle.dump([files_pickle, sections_pickle], saveFile)
    return files_pickle, sections_pickle


def mostRelevantTag(name, res_dict):
    for pre_defined_sections in res_dict.keys():
        res_dict[pre_defined_sections] = get_jaccard_sim(name, pre_defined_sections)
    max_value = max(res_dict.values())  # maximum value
    if max_value == 0:
        return -1
    max_keys = [k for k, v in res_dict.items() if v == max_value]  # getting all keys containing the `maximum`
    return max_keys


def process_corpus(corpus):
    local_jaccard_dict = init_sectionNames_dict('float')
    dict_sections = init_sectionNames_dict()
    counterFile = 1
    counterSize = len(corpus)
    for file in corpus.keys():
        print('Processing Corpus {0}/{1}'.format(counterFile, counterSize))
        for section in corpus[file].keys():
            keys = mostRelevantTag(section, local_jaccard_dict)
            if keys == -1:
                continue
            for key in keys:
                if not corpus[file][section]:  # Check if trying to add empty list
                    break
                dict_sections[key].append((file, corpus[file][section]))
        counterFile += 1
    print('Done!')
    return dict_sections


# files, sections = loadCorpus('corpus.pickle')
# process_corpus(files)
# print()

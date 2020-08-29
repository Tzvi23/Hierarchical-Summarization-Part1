"""
This script will process the pickle files
That contain all the data collected during classification of section file
Each pickle contains list of tuples as follows:
(Sentence Number, Sentence Text, Topic, Score, 0 - Satellite / 1 - Nucleus)
"""

import pickle
import os
import math

def look_for(this):
    tuple_index = ['sentence_number', 'sentence_text', 'topic', 'score', 'class']
    return tuple_index.index(this)


def load_data(file_name, modelNumber, topicClass_dir='output/topic_class'):
    dataPath = os.path.join(os.path.join(topicClass_dir, str(modelNumber)), 'textData')
    try:
        with open(os.path.join(dataPath, file_name + '.pickle'), mode='rb') as pFile:
            return pickle.load(pFile)
    except FileNotFoundError as error:
        print(error)


def sort_list(cData, index, descending=False):
    cData.sort(key=lambda sent: sent[index], reverse=descending)


def shorten_text(cData, min_length, percentage):
    if len(cData) >= min_length:
        sort_list(cData, look_for('score'), descending=True)
        size = int(math.ceil(len(cData) * percentage))
        updated_list = cData[:size]
        sort_list(updated_list, look_for('sentence_number'), descending=False)
        return updated_list


def shorten_text2(cData, min_length, percentage, topic_number):
    if len(cData) >= min_length:
        # All the sentences that not in the topic_number set to 0
        for _ in range(len(cData)):
            if cData[_][3] != topic_number:
                cData[_] = (cData[_][0], cData[_][1], 0, cData[_][3])
        sort_list(cData, 2, descending=True)
        size = int(math.ceil(len(cData) * percentage))
        updated_list = cData[:size]
        sort_list(updated_list, 0, descending=False)
        return updated_list


def get_score(cData, text):
    index = [x for x, y in enumerate(cData) if y[1] == text]
    return cData[index[0]][3] , cData[index[0]][5]

# data = load_data('6101_governance_statement_strip_output.txt.pickle', 4)
# data = shorten_text(data, 2, 0.5)
# print(data)

import os
import csv
import pickle
from pathlib import Path
import LDA_classifier as classifier
from print_colors import bcolors

# Change working directory
def change_working_dir():
    work_str = Path(os.getcwd())
    os.chdir(work_str.parent)

# change_working_dir()

# Directory that contains all the CSV files for each file with topic/text data
OUTPUT_FINAL_STAGE_PATH = 'output/final_stage'
TOPIC_MODEL = 10
FILE_ID = 65

# region Model loading
MODEL_PATH = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gensim_models/10topics/lda_model_trained_10topics.model'
DATA_DIR = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gensim_files/10Topic'

# Working with 10 topic model
def load_LDA_model(topic_model, topic_data_dir):
    classifier.load_Model_local(topic_model)
    classifier.load_data_local(topic_data_dir)
    classifier.print_model_topics()
    print(f'{bcolors.HEADER} \t [!!]\tLDA model loaded!\t[!!] {bcolors.ENDC}')
# endregion

if classifier.current_model is None:
    load_LDA_model(topic_model=MODEL_PATH, topic_data_dir=DATA_DIR)

def read_file(topic_model, file_id, output_final_stage_path):
    """
    Reads the final stage file CSV and converts to specific dictionary.
    File
        -> Section 1
            -> Topic1 ; Nucleus Text
            -> Topic2 ; Nucleus Text
        -> Section 2
            -> Topic3 ; Nucleus Text
    """
    def process_section_name(sectName):
        tmp = sectName.split('_')[1:] # Remove the file id
        remove = ['strip', 'processed', 'output']
        return '_'.join([w for w in tmp if w not in remove])

    # File dict data
    file_nucleus = dict()

    # Create dir path string for the CSV read
    file_dir_path = os.path.join(os.path.join(output_final_stage_path, str(topic_model)), str(file_id))

    for section_file in os.listdir(file_dir_path):
        current_section_name = process_section_name(section_file[:-4])
        file_nucleus[current_section_name] = dict()

        section_path = os.path.join(file_dir_path, section_file)  # Full path to specific section CSV file
        with open(section_path, 'r') as sectFile:
            csv_reader = csv.DictReader(sectFile)
            for row in csv_reader:
                file_nucleus[current_section_name][int(row['topic_number'])] = row['Nucleus_text']

    return file_nucleus

# file_csv_dict = read_file(topic_model=TOPIC_MODEL, file_id=FILE_ID, output_final_stage_path=OUTPUT_FINAL_STAGE_PATH)

# Scoring
def score_topics(data):
    """
    Scores and sorts the sections topics using the loaded LDA model
    """
    def sort_tuple(tup):
        tup.sort(key=lambda x: x[1], reverse=True)
        return tup

    topic_rank = dict()
    for section, topics in data.items():
        topic_rank[section] = list()
        for topic in topics:
            topic_rank[section].append((topic, classifier.score_topic(current_text=topics[topic], topic_number=topic)))
        topic_rank[section] = sort_tuple(topic_rank[section])  # Sort the list by score

    return topic_rank

# res = score_topics(data=file_csv_dict)

def score_fileID(fileId, topicModel=10):
    print(f'{bcolors.OKGREEN}\t\tProcessing file id: {fileId}{bcolors.ENDC}')
    file_csv_dict = read_file(topic_model=topicModel, file_id=fileId, output_final_stage_path=OUTPUT_FINAL_STAGE_PATH)
    res = score_topics(data=file_csv_dict)
    return file_csv_dict, res


# region <---- Second Approach NI x TI ---->
TOPIC_CLASS = '/home/tzvi/PycharmProjects/HSdataprocessLinux/output/scores'

def load_pickle_data(file_id, modelNumber):
    basePath = Path(TOPIC_CLASS)
    modelFolder = basePath / str(modelNumber)

    file_data = dict()
    for file in os.listdir(modelFolder):
        if file.split('_')[0] == str(file_id):  # Check if the file id corresponds to file_id
            with open(modelFolder / file, mode='rb') as dataFile:
                section_name = '_'.join(file.split('_')[1:-3])  # Extract section name from the file name
                file_data[section_name] = pickle.load(dataFile)
    return file_data

def process_score_data(file_score):
    """
    Creates a list of all the text nodes with new score: NS x TI and sorts them by the new score
    :param file_score: Dictionary with all the sections and tuples data
    :return:
    """
    total_score = list()
    for section in file_score.keys():
        for sent in file_score[section]:
            if sent[5] == 'N':
                v_score = dict(sent[6])[sent[3]]  # Get topic score in vector
                s_score = sent[4] * v_score  # NI * TI
                total_score.append((sent[2], s_score, len(sent[2].split())))
    total_score.sort(key=lambda x: x[1], reverse=True)
    return total_score

def create_summary_NSxTI(fileId, modelNumber, maxWords=1000):
    file_score_data = load_pickle_data(file_id=fileId, modelNumber=modelNumber)
    textData = process_score_data(file_score_data)
    new_text = list()
    counter = 0
    for sent in textData:
        if (sent[0] + '.').capitalize() in new_text or sent[0].capitalize() in new_text:
            continue
        if counter + sent[2] <= maxWords:
            cur_sent = sent[0]
            if not cur_sent.endswith('.'):
                cur_sent = cur_sent + '.'
            new_text.append(cur_sent.capitalize())
            counter += sent[2]
    write_text_to_file(fileId=fileId, newSummary=new_text)

def write_text_to_file(fileId, newSummary):
    OUTPUT_SUMMARY_PATH = Path('/home/tzvi/PycharmProjects/HSdataprocessLinux/summarizerWS/summaries_NuVec_NI_TI')
    with open(OUTPUT_SUMMARY_PATH / (str(fileId) + '_NuVec_NI_TI.txt'), mode='w') as outFile:
        outFile.writelines(newSummary)

# create_summary_NSxTI(fileId=26464, modelNumber=10)
def run_dataSet():
    DATA_PATH = '/home/tzvi/PycharmProjects/HSdataprocessLinux/data'
    queue = [file[:-4] for file in os.listdir(DATA_PATH)]

    for file in queue:
        print(f'{bcolors.OKGREEN}Processing: {file}{bcolors.ENDC}')
        create_summary_NSxTI(fileId=int(file), modelNumber=10)

run_dataSet()

# endregion


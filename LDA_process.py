import csv
import pickle
import LDA_classifier as classifier
import pprint
import subprocess
import json
import os
from print_colors import bcolors
from project_config import parser


def strip_name(input_name):
    name = input_name.replace('(', '').replace(')', '').split()  # Remove ( ) and split by space
    node_type = name[0].split('ENDNODENUM')[1]  # Nucleus or Satellite
    node_edge = name[1]  # leaf or other
    node_number = name[2]  # leaf number
    node_relation = name[4]  # rel2par
    return [node_type, node_edge, node_number, node_relation]


def recursive_read_list(json_output):
    test_list = []
    if len(json_output) == 1:
        content = json_output['name']
        content = content.split('|')
        content_text = content[1][6:].strip()  # Leaf text
        content_leaf = content[0]
        [node_type, node_edge, node_number, node_relation] = strip_name(content_leaf)
        # test_list.append((content_text, node_edge + node_number, node_type, node_relation))
        return content_text, node_edge + node_number, node_type, node_relation
    test_list.append(recursive_read_list(json_output['children'][0]))
    test_list.append(recursive_read_list(json_output['children'][1]))
    return test_list


def recursive_read_text(json_output, results_dict_list, counter, text_tuples, mode='LDA', node_filter=None):
    text_output = ""
    if len(json_output) == 1:
        content = json_output['name']
        content = content.split('|')
        content_text = content[1][6:].strip()  # Leaf text
        content_leaf = content[0]
        [node_type, node_edge, node_number, node_relation] = strip_name(content_leaf)
        if node_filter is None:
            counter += 1
            topic_class, sent_score, topic_vector = classifier.classify_LDA_model_oneSentence(content_text, mode)
            text_tuples.append((counter, content_text, topic_class, sent_score, 1 if node_type == 'Nucleus' else 0, topic_vector))
            results_dict_list.append(topic_class)
            json_output['name'] = json_output['name'] + ' | Topic: ' + str(topic_class)
            return counter
        elif node_filter == node_type:
            return text_output + ' ' + content_text
        else:
            return text_output
    counter = recursive_read_text(json_output['children'][0], results_dict_list, counter, text_tuples, mode,
                                  node_filter)
    if len(json_output['children']) > 1:
        counter = recursive_read_text(json_output['children'][1], results_dict_list, counter, text_tuples, mode,
                                      node_filter)
    return counter


def loop_discourse_results(topic_number, mode='LDA',
                           discourse_output_dir=parser.get('LDA_process', 'loop_discourse_results_one_file_discourse_output_dir')):
    results_dict = dict()
    counter = 0
    for discourse_results in os.listdir(discourse_output_dir):
        if os.path.isdir(os.path.join(discourse_output_dir, discourse_results)):
            continue
        if 'strip_output' in discourse_results and 'FAILED_PARSE' not in discourse_results and 'FAILED_SEG' not in discourse_results:
            results_dict[discourse_results[:-17]] = list()
            text_tuples = list()
            classify_discourse_tree(discourse_results, results_dict[discourse_results[:-17]], discourse_output_dir,
                                    topic_number, text_tuples, mode=mode)
    if mode == 'LDA':
        write_stats_to_file(results_dict, topic_number + 1)
    elif mode == 'HLDA':
        write_stats_to_file_hlda(results_dict)


def write_stats_to_file_hlda(results_dict):
    # Find all the fieldnames possible
    fieldnames = ['number file']
    for key in results_dict.keys():
        for topic in results_dict[key]:
            if topic not in fieldnames:
                fieldnames.append(topic)
    fieldnames.append('file name')
    # Create base dict
    writer_dict = dict()
    total_dict = dict()
    for field_name in fieldnames:
        writer_dict[field_name] = 0
        total_dict[field_name] = 0
    total_dict['number file'] = 'Total'
    total_dict.pop('file name')

    with open('topic_stats_HLDA.csv', mode='w') as stats_file:
        writer = csv.DictWriter(stats_file, fieldnames=fieldnames)
        writer.writeheader()

        file_counter = 0
        for file_name in results_dict:
            file_counter += 1
            writer_dict['number file'] = file_counter
            writer_dict['file name'] = file_name
            for item in results_dict[file_name]:
                writer_dict[item] += 1
                total_dict[item] += 1
            writer.writerow(writer_dict)
            writer_dict = {key: 0 for key in writer_dict}  # reset the dict values
        writer.writerow(total_dict)


def classify_discourse_tree(filename, results_dict_list, dis_dir, topicNumber, text_tuples, mode='LDA',
                            script_path=parser.get('LDA_process', 'classify_discourse_tree_script_path')):
    dir_path = os.path.join('output/topic_class', str(topicNumber))
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    print(bcolors.OKGREEN + 'Classifying topics for file: ' + filename + bcolors.ENDC)
    file_name = filename[:-4]
    file_path = os.path.join(dis_dir, filename)
    parsing_output = subprocess.check_output(['python2', script_path, file_path])
    parsed_json = json.loads(parsing_output)
    sent_counter = 0
    sent_counter = recursive_read_text(parsed_json, results_dict_list, sent_counter, text_tuples, mode=mode)
    # with open(os.path.join('output/topic_class', file_name + '_topic.txt'), mode='w') as output:
    with open(os.path.join(dir_path, file_name + '_topic.txt'), mode='w') as output:
        json.dump(parsed_json, output)
    # write file data to pickle item
    pickle_path = os.path.join(dir_path, 'textData')
    if not os.path.exists(pickle_path):
        os.mkdir(pickle_path)
    with open(os.path.join(pickle_path, filename + '.pickle'), mode='wb') as pickle_file:
        pickle.dump(text_tuples, pickle_file)


def write_stats_to_file(data, numOfTopics, filename='topic_stats'):
    with open(filename + '_' + str(numOfTopics - 1) + '.csv', mode='w') as stats_file:
        stats_writer = csv.writer(stats_file, delimiter=',')
        # header = 'Number file', '0', '1', '2', '3', '-1'
        header = [str(x) for x in range(numOfTopics - 1)]
        header.insert(0, 'Number file')
        header.insert(len(header), '-1')
        totals = [0] * numOfTopics
        stats_writer.writerow(header)

        counter = 0
        for key in data:
            counter += 1
            sub_data = list()
            sub_data.append(counter)
            for x in range(numOfTopics - 1):
                count = data[key].count(x)
                totals[x] += count
                sub_data.append(count)
            count = data[key].count(-1)
            totals[numOfTopics - 1] += count
            sub_data.append(count)

            # Get stats
            negative, zero, one, two, three = data[key].count(-1), data[key].count(0), data[key].count(1), data[
                key].count(2), data[key].count(3)

            # sub_data = list()
            # sub_data.append(counter)
            # sub_data.append(negative)
            # sub_data.append(zero)
            # sub_data.append(one)
            # sub_data.append(two)
            # sub_data.append(three)

            sub_data.append(key)
            for item in data[key]:
                sub_data.append(str(item))
            stats_writer.writerow(sub_data)
        totals = [str(item) for item in totals]
        totals.insert(0, 'Totals')
        stats_writer.writerow(totals)


def loop_models():
    topic_4_model = 'gensim_models/4topics/lda_model_trained_4topics.model'
    topic_4_data_dir = 'gensim_files/4Topic'
    topic_6_model = 'gensim_models/6topics/lda_model_trained_6topics.model'
    topic_6_data_dir = 'gensim_files/6Topic'
    topic_10_model = 'gensim_models/10topics/lda_model_trained_10topics.model'
    topic_10_data_dir = 'gensim_files/10Topic'
    hdp_model = 'gensim_models/hdp_model.model'

    # 4 topics model
    classifier.load_Model_local(topic_4_model)
    classifier.load_data_local(topic_4_data_dir)
    classifier.print_model_topics()
    loop_discourse_results(4, mode='LDA')

    # 6 topics model
    classifier.load_Model_local(topic_6_model)
    classifier.load_data_local(topic_6_data_dir)
    classifier.print_model_topics()
    loop_discourse_results(6, mode='LDA')

    # 10 topics model
    classifier.load_Model_local(topic_10_model)
    classifier.load_data_local(topic_10_data_dir)
    classifier.print_model_topics()
    loop_discourse_results(10, mode='LDA')

    # HDP model
    classifier.load_Model_local(hdp_model)
    classifier.load_data_local(topic_4_data_dir)
    classifier.print_model_topics()
    loop_discourse_results(20, mode='HLDA')


"""
< ------ One file functions ------- >
"""
# region one file functions
def loop_models_one_file(models_choice, **params):
    def loop_discourse_results_one_file(topic_number, fileId, mode='LDA',
                                        discourse_output_dir=parser.get('LDA_process', 'loop_discourse_results_one_file_discourse_output_dir')):
        results_dict = dict()  # each file processed and list of all the topics detected
        for discourse_results in os.listdir(discourse_output_dir):
            # If the current file is a dir => continue
            if os.path.isdir(os.path.join(discourse_output_dir, discourse_results)):
                continue
            # If the current file is not he fileID we looking for => continue
            if discourse_results.split('_')[0] != fileId:
                continue
            # If the current file has the FAILED_PARSE or FAILED_SEG we cannot process => continue
            if 'strip_output' in discourse_results and 'FAILED_PARSE' not in discourse_results and 'FAILED_SEG' not in discourse_results:
                results_dict[discourse_results[:-17]] = list()
                text_tuples = list()
                classify_discourse_tree(discourse_results, results_dict[discourse_results[:-17]], discourse_output_dir,
                                        topic_number, text_tuples, mode=mode)
        if mode == 'LDA':
            write_stats_to_file(results_dict, topic_number + 1)
        elif mode == 'HLDA':
            write_stats_to_file_hlda(results_dict)

    # Checks if all the values exists in params
    if len(params) != 8:
        print('ERROR - missing input values')
        raise ValueError('ERROR - missing input values')

    # File id to process
    file_id = params['file_id']

    # Paths
    topic_4_model = params['topic_4_model']
    topic_4_data_dir = params['topic_4_data_dir']
    topic_6_model = params['topic_6_model']
    topic_6_data_dir = params['topic_6_data_dir']
    topic_10_model = params['topic_10_model']
    topic_10_data_dir = params['topic_10_data_dir']
    hdp_model = params['hdp_model']

    # classifier.clear_variables()
    if models_choice['4'] is True:
        # 4 topics model
        classifier.load_Model_local(topic_4_model)
        classifier.load_data_local(topic_4_data_dir)
        classifier.print_model_topics()
        loop_discourse_results_one_file(4, file_id, mode='LDA')

    if models_choice['6'] is True:
        # 6 topics model
        classifier.load_Model_local(topic_6_model)
        classifier.load_data_local(topic_6_data_dir)
        classifier.print_model_topics()
        loop_discourse_results_one_file(6, file_id, mode='LDA')

    if models_choice['10'] is True:
        # 10 topics model
        if classifier.current_model is None:
            classifier.load_Model_local(topic_10_model)
            classifier.load_data_local(topic_10_data_dir)
            classifier.print_model_topics()
        loop_discourse_results_one_file(10, file_id, mode='LDA')

    if models_choice['hdp'] is True:
        # HDP model
        classifier.load_Model_local(hdp_model)
        classifier.load_data_local(topic_4_data_dir)
        classifier.print_model_topics()
        loop_discourse_results_one_file(20, file_id, mode='HLDA')

# endregion

# region Testing
# loop_models_one_file(topic_4_model='gensim_models/4topics/lda_model_trained_4topics.model',
#                      topic_4_data_dir='gensim_files/4Topic',
#                      topic_6_model='gensim_models/6topics/lda_model_trained_6topics.model',
#                      topic_6_data_dir='gensim_files/6Topic',
#                      topic_10_model='gensim_models/10topics/lda_model_trained_10topics.model',
#                      topic_10_data_dir='gensim_files/10Topic',
#                      hdp_model='gensim_models/hdp_model.model')
# loop_models()
# enregion

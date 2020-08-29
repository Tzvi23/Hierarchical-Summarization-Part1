from summarizerWS import topicRanker as tr
import os
import math

MAX_WORD = 100
MAX_FILE = 1000

def count_words(data):
    for topic_name, topics in data.items():
        for topic_number, topic_txt in topics.items():
            tmp_txt = topic_txt.split('.')
            tmp_txt = [txt.strip() for txt in tmp_txt]  # Strip edges
            count_txt = list()
            for txt in tmp_txt:
                if not len(txt.split()):
                    continue
                count_txt.append((txt, len(txt.split())))
            data[topic_name][topic_number] = count_txt

def total_topic_importance_calc(topic_scoring, model=10):
    # Create base dict
    total_topic = dict([(x, 0) for x in range(model)])
    for topic_name, scores in topic_scoring.items():
        tmp = dict(scores)
        for key in tmp.keys():
            total_topic[key] += tmp[key]
    total_topic = [(k, v) for k, v in total_topic.items()]  # Convert dict to list of tuples
    total_topic.sort(key=lambda x: x[1], reverse=True)
    return total_topic

def process_data(total_topic_data, model=10):
    # Create base dict
    total_data_by_topic = dict([(x, list()) for x in range(model)])
    for section in total_topic_data.keys():
        for topic in total_topic_data[section]:
            for sent in total_topic_data[section][topic]:
                total_data_by_topic[topic].append(sent)
    return total_data_by_topic

def data_topic_length(topic_scores):
    global MAX_WORD
    count = 0
    for x in topic_scores:
        if x[1] > 0:
            count += 1
    MAX_WORD = math.floor(MAX_FILE / count)

def build_summary(data, topicImportance):
    summary = list()
    x = total_topic_importance_calc(topicImportance, model=10)
    y = process_data(data, model=10)
    data_topic_length(x)

    word_count = 0
    for index in range(len(x)):  # To make sure that we go in order from start to finish
        topic_number = x[index][0]
        if len(y[topic_number]):
            topic_word_count = 0
            for sent in y[topic_number]:
                if word_count + sent[1] <= MAX_FILE and topic_word_count + sent[1] <= MAX_WORD:
                    summary.append(sent[0] + '. ')
                    word_count += sent[1]
                    topic_word_count += sent[1]
                else:
                    break
    # for topic_name, scores in topicImportance.items():
    #     count = 0
    #     for topic_number, score in scores:
    #         for sent in data[topic_name][topic_number]:
    #             if count + sent[1] > MAX_WORD:
    #                 break
    #             else:
    #                 summary.append(sent[0] + '.')
    #                 count += sent[1]
    return summary

"""
Main function
Creates a summary for specific file based on ranking of each topic in each section.
Each section can add up to 100 words based on MAX_WORD variable
"""
def create_summary(file_id, des_dir='/home/tzvi/PycharmProjects/HSdataprocessLinux/summarizerWS/summaries'):
    file_data, topic_score = tr.score_fileID(file_id)
    count_words(file_data)
    new_summary = build_summary(file_data, topic_score)
    with open(os.path.join(des_dir, str(file_id) + '.txt'), 'w') as output_file:
        output_file.writelines(new_summary)


# create_summary(26464)

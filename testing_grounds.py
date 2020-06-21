"""
This code is for testing clustering evaluation.
1. Finish to process the files.
2. Do clustering on the original files.
3. Do clustering on the processed files.
"""
import main_pipeline as mp
import csv
from clusters.cluster_engine_updated import run_kmeans
from clusters.corpus_creator import create_clustering_corpus
import os
from print_colors import bcolors
import numpy as np
import pandas as pd


def create_confusion_matrix(ground_truth, process_files):
    def find_cluster(processed_files, elem):
        for cluster in process_files.keys():
            if elem in processed_files[cluster]:
                return cluster
        return -1

    CM = np.zeros((4, 4))
    for cluster in ground_truth.keys():
        for label in ground_truth[cluster]:
            CM[cluster, find_cluster(process_files, label)] += 1

    # Calculate Purity I
    C1 = np.max(CM[0, :])
    C2 = np.max(CM[1, :])
    C3 = np.max(CM[2, :])

    # Sum all rows values
    for row in range(3):
        CM[row, 3] = np.sum(CM[row, :])
    # Sum all columns rows
    for col in range(3):
        CM[3, col] = np.sum(CM[:, col])
    # Calculate corner value
    CM[3, 3] = np.sum(CM[3, :])

    # Precision = TP/(TP+FP)
    precision = {0: 0, 1: 0, 2: 0}
    for cluster in precision.keys():
        precision[cluster] = CM[cluster, cluster] / CM[3, cluster]
    print(f'Precision: {precision}')

    # Recall = TP/(TP+FN)
    recall = {0: 0, 1: 0, 2: 0}
    for cluster in recall.keys():
        recall[cluster] = CM[cluster, cluster] / CM[cluster, 3]
    print(f'Recall: {recall}')

    # Average precision
    avg_precision = 0
    for cluster in precision.keys():
        avg_precision += precision[cluster] * CM[cluster, 3]
    avg_precision = avg_precision / CM[3, 3]
    print(f'Average precision: {avg_precision}')

    # Average recall
    avg_recall = 0
    for cluster in recall.keys():
        avg_recall += recall[cluster] * CM[3, cluster]
    avg_recall = avg_recall / CM[3, 3]
    print(f'Average recall: {avg_recall}')

    # Calculate purity II
    purity = (C1 + C2 + C3) / CM[3, 3]
    print(f'Purity: {purity}')

    # Calculate F1 Score
    f1_score = {0: 0, 1: 0, 2: 0}
    for cluster in precision.keys():
        f1_score[cluster] = 2 * ((precision[cluster] * recall[cluster]) / (precision[cluster] + recall[cluster]))
    print(f'F1_score: {f1_score}')

    print(CM)
    return {'confusion_matrix': CM,
            'precision': precision,
            'recall': recall,
            'avg_precision': avg_precision,
            'avg_recall': avg_recall,
            'purity': purity,
            'f1_score': f1_score}


def processed_list(log_file):
    """
    Creates list of files that has been processed based on the log file provided
    """
    file_list = list()
    with open(log_file, 'r') as logFile:
        csv_reader = csv.reader(logFile, delimiter=',')
        for row in csv_reader:
            if row[1] not in file_list and (row[0] == 'end' or row[0] == 'proc'):
                file_list.append(row[1])
    return file_list


def check_files(proc_list, discourse_output_path='/home/tzvi/PycharmProjects/linuxDiscourse/src/Output'):
    """
    Makes sure that there files in the output dir that correspond with the proc_list
    If files are missing, removes the file name from the proc_list
    """
    # Make list of all files in the output dir
    output_list = list()
    for file in os.listdir(discourse_output_path):
        if file.split('_')[0] not in output_list:
            output_list.append(file.split('_')[0] + '.txt')
    # Check difference
    diff = list(set(proc_list) - set(output_list))
    # remove from proc_list file names that not been processed
    for filename in diff:
        proc_list.pop(proc_list.index(filename))


def evaluation_list(eval_dir):
    eval_list = list()
    for file in os.listdir(eval_dir):
        eval_list.append(file.replace('_nucleus', ''))
    return eval_list


def cluster_eval(config_file=None):
    # Get list of all processed files
    proc_files = processed_list('logs/D29_04_20M17_37.txt')
    print(proc_files)
    check_files(proc_files)
    # Process all the files that finished discourse parsing
    # third stage & four stage
    """
    for file_id in proc_files:
        f_id = int(file_id[:-4])  # remove .txt and convert to int value
        if config_file is None:
            # run stages
            mp.third_stage(f_id, {'4': True, '6': False, '10': False, 'hdp': False})
            mp.fourth_stage(f_id)
            mp.show_case(f_id, 4)
        else:
            argument_list = [
                config_file['third_stage']['models'],
                config_file['third_stage']['models_path']
            ]
            mp.third_stage(f_id, argument_list)  # Working on all of the models
            # Fourth stage
            # mp.fourth_stage(f_id)
            for key in config_file['third_stage']['models'].keys():
                if config_file['third_stage']['models'][key] is True:
                    mp.fourth_stage(f_id, key)
                    mp.show_case(f_id, int(key))
    """
    input('Finished processing - press space+enter')

    proc_files = evaluation_list('/home/tzvi/PycharmProjects/HSdataprocessLinux/show_case/final_report/4/nucleus')

    create_clustering_corpus('data/',
                             '/home/tzvi/PycharmProjects/HSdataprocessLinux/clusters',
                             file_name='corpus.csv')

    print('Finished processing the data\nStarting to cluster....')
    # Calculate clustering for the current <!-original-!> files
    print(f'{bcolors.WARNING}Clustering original files{bcolors.ENDC}')
    truth, original_M = run_kmeans('/home/tzvi/PycharmProjects/HSdataprocessLinux/clusters/corpus.csv',
                                   '/home/tzvi/PycharmProjects/HSdataprocessLinux/clusters/output_plots',
                                   proc_files,
                                   'clustering_report.txt')

    print(f'{bcolors.WARNING}Creating new corpus{bcolors.ENDC}')
    # Create new clustering corpus from the processed files
    create_clustering_corpus('/home/tzvi/PycharmProjects/HSdataprocessLinux/show_case/final_report/4/nucleus',
                             '/home/tzvi/PycharmProjects/HSdataprocessLinux/clusters')

    print(f'{bcolors.WARNING}Clustering for processed files{bcolors.ENDC}')
    # Calculate clustering for the current <!-processed-!> files
    predict, predict_M = run_kmeans('/home/tzvi/PycharmProjects/HSdataprocessLinux/clusters/after_corpus.csv',
                                    '/home/tzvi/PycharmProjects/HSdataprocessLinux/clusters/after_output_plots',
                                    proc_files,
                                    'after_clustering_report.txt')

    report = create_confusion_matrix(truth, predict)

    with open('after_clustering_report.txt', 'a') as report_file:
        for key in report.keys():
            report_file.write('\n' + key + '\n' + str(report[key]))

    report_df = pd.DataFrame([original_M, pred_M, report], index=['Texts', 'Summaries', 'report'])
    report_df.to_excel("eval_report.xlsx")


# cluster_eval()

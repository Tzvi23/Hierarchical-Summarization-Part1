"""
This is the main pipeline script
"""
from project_config import parser

def convert_topics_for_show_case(modelNumber=10):
    from final_stage import topic_labels
    import json
    topics = topic_labels[str(modelNumber)]
    for topic in topics.keys():
        topics[topic] = topics[topic].split('|')
        topics[topic] = [w.strip() for w in topics[topic]]
    return json.dumps(topics)
"""
First Stage
1. Load the original file to be processed.
2. Pre process the original file to xml format and pure text from the xml file.
"""


def first_stage(inputFile_path, discourseInput=parser.get('main_pipeline', 'discourseInput')):
    import preprocess

    preprocess.pre_process_single_file(inputFile_path, discourseInput)


"""
Second Stage
Using the discourse project by running the main script of the project with arguments.
1. Split the xml file to separate file based on section in the xml file.
2. Try discourse each of the section files.
"""


def second_stage(xml_result_path, discourse_script_path=parser.get('main_pipeline', 'discourse_script_path')):
    import os
    os.system(' '.join(['python2', discourse_script_path, xml_result_path]))
    # subprocess.call([discourse_script_path, xml_result_path], shell=True)
    # subprocess.check_output(['python2', discourse_script_path, xml_result_path])


"""
Third Stage
Classify the text nodes in the discourse result tree files for all the sections.
Based on pre-trained LDA models.
"""


def third_stage(file_id, models=None):
    from LDA_process import loop_models_one_file
    if isinstance(models, list):  # It means CLI MODE
        models[1]["file_id"] = str(file_id)
        loop_models_one_file(models[0], **models[1])  # 0 - Models, 1 - Topic Paths
    else:
        loop_models_one_file(models,
                             file_id=str(file_id),
                             topic_4_model=parser.get('main_pipeline', 'topic_4_model'),
                             topic_4_data_dir=parser.get('main_pipeline', 'topic_4_data_dir'),
                             topic_6_model=parser.get('main_pipeline', 'topic_6_model'),
                             topic_6_data_dir=parser.get('main_pipeline', 'topic_6_data_dir'),
                             topic_10_model=parser.get('main_pipeline', 'topic_10_model'),
                             topic_10_data_dir=parser.get('main_pipeline', 'topic_10_data_dir'),
                             hdp_model=parser.get('main_pipeline', 'hdp_model')
                             )


"""
Fourth Stage
In this stage the program will process the discourse tree after topic classification and create units of
small sub units in the tree. Each unit will have number of leaf nodes of the original discourse tree.
Each unit will have only one topic number after calculating the weights of the nodes in the same unit.
The calculation will be determined by effected by each node and if it Nucleus or Satellite and the place of the node
in the hierarchy of the unit being built.
"""


def fourth_stage(file_id, model_number=None):
    from final_stage import loop_topic_data
    loop_topic_data(file_id, model_number)


"""
Show case stage
This stage is just a summary processes to show the results to the user in a simple way.
This stage collects all the data needed and parse it in json formats and creates an
.html file view of the results.
"""


def show_case(file_id, model_number, topic_words=None):
    from show_case.show_case_functions import run_show_case
    show_case_url = run_show_case(file_id, model_number,
                                  original_text_dir=parser.get('main_pipeline', 'original_text_dir'),
                                  xml_processed_dir=parser.get('main_pipeline', 'xml_processed_dir'),
                                  xml_parse_dir=parser.get('main_pipeline', 'xml_parse_dir'),
                                  topic_class_dir=parser.get('main_pipeline', 'topic_class_dir'),
                                  trees_dir=parser.get('main_pipeline', 'trees_dir'),
                                  final_stage_dir=parser.get('main_pipeline', 'final_stage_dir'),
                                  topic_data=convert_topics_for_show_case(model_number)
                                  )
    return show_case_url


# first_stage('data/25082.txt')
# second_stage('2326.txt.xml')
# third_stage(92, {'4': True, '6': False, '10': False, 'hdp': False})
# fourth_stage(28080, '4')
# show_case(25110, 10)

def run_last_stages():

    from summarizerWS import summarizer
    import os

    SUMMARY_FOLDER = '/home/tzvi/PycharmProjects/HSdataprocessLinux/summarizerWS/summaries'
    proc_file = [file[:-4] for file in os.listdir(SUMMARY_FOLDER)]

    topic_word_list = convert_topics_for_show_case()
    DATA_PATH = '/home/tzvi/PycharmProjects/HSdataprocessLinux/data'
    queue = [file[:-4] for file in os.listdir(DATA_PATH)]
    # Run stages: fourth stage + show_case
    for fileid in queue:
        if fileid in proc_file:
            continue
        third_stage(file_id=int(fileid), models={'4': False, '6': False, '10': True, 'hdp': False})
        fourth_stage(file_id=int(fileid), model_number='10')

        summarizer.create_summary(int(fileid))
        show_case(file_id=int(fileid), model_number=10, topic_words=topic_word_list)
    print('END')

# run_last_stages()

# Temp stat code
# from pathlib import Path
# import os
# d = Path('data')
# for file in os.listdir(d):
#     first_stage(str(d / file))

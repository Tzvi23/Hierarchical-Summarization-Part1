"""
This is the main pipeline script
"""

"""
First Stage
1. Load the original file to be processed.
2. Pre process the original file to xml format and pure text from the xml file.
"""


def first_stage(inputFile_path, discourseInput='/home/tzvi/PycharmProjects/linuxDiscourse/src/Input/xml/'):
    import preprocess

    preprocess.pre_process_single_file(inputFile_path, discourseInput)


"""
Second Stage
Using the discourse project by running the main script of the project with arguments.
1. Split the xml file to separate file based on section in the xml file.
2. Try discourse each of the section files.
"""


def second_stage(xml_result_path, discourse_script_path='/home/tzvi/PycharmProjects/linuxDiscourse/src/main_src.py'):
    import os
    os.system(' '.join(['python2', discourse_script_path, xml_result_path]))
    # subprocess.call([discourse_script_path, xml_result_path], shell=True)
    # subprocess.check_output(['python2', discourse_script_path, xml_result_path])


"""
Third Stage
Classify the text nodes in the discourse result tree files for all the sections.
Based on pre-trained LDA models.
"""


def third_stage(file_id, models):
    from LDA_process import loop_models_one_file
    loop_models_one_file(models,
                         file_id=str(file_id),
                         topic_4_model='gensim_models/4topics/lda_model_trained_4topics.model',
                         topic_4_data_dir='gensim_files/4Topic',
                         topic_6_model='gensim_models/6topics/lda_model_trained_6topics.model',
                         topic_6_data_dir='gensim_files/6Topic',
                         topic_10_model='gensim_models/10topics/lda_model_trained_10topics.model',
                         topic_10_data_dir='gensim_files/10Topic',
                         hdp_model='gensim_models/hdp_model.model'
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


def show_case(file_id, model_number):
    from show_case.show_case_functions import run_show_case
    show_case_url = run_show_case(file_id, model_number,
                                  original_text_dir='/home/tzvi/PycharmProjects/HSdataprocessLinux/data',
                                  xml_processed_dir='/home/tzvi/PycharmProjects/HSdataprocessLinux/output/text_xml',
                                  xml_parse_dir='/home/tzvi/PycharmProjects/HSdataprocessLinux/output/xmlParse',
                                  topic_class_dir='/home/tzvi/PycharmProjects/HSdataprocessLinux/output/topic_class',
                                  trees_dir='/home/tzvi/PycharmProjects/linuxDiscourse/src/Output',
                                  final_stage_dir='/home/tzvi/PycharmProjects/HSdataprocessLinux/output/final_stage_graph'
                                  )
    return show_case_url

# first_stage('data/130.txt')
# second_stage('130.txt.xml')
# third_stage(130)
# fourth_stage(130)
# show_case(130, 10)

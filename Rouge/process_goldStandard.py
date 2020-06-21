import os
from utils.util_functions import re_structure_text
from utils.util_functions import create_txt_file

gold_standard_full_dir_path = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_summaries'
# Full text rouge eval
output_dir_full_path = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/full_text'
gold_pre_process_full_dir_path = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/pre_process_'

if not os.path.exists(output_dir_full_path):
    os.mkdir(output_dir_full_path)

# Merge each gold standard file to one
def merge_files(gold, output):
    file_text = dict()
    for file in os.listdir(gold):
        print(file)
        file_id, section_num = file.split('_')[0], int(file.split('_')[1][:-4])
        if file_id not in file_text:
            file_text[file_id] = dict()
        with open(os.path.join(gold, file), mode='r') as gold_file:
            file_text[file_id][section_num] = gold_file.read().strip()
    for file_name in file_text.keys():
        txt = ''
        section_list = list(file_text[file_name].keys())
        section_list.sort()
        for section_name in section_list:
            if not txt:
                txt += file_text[file_name][section_name]
            else:
                txt += '\n'
                txt += file_text[file_name][section_name]
        with open(os.path.join(output, file_name) + '.txt', mode='w') as output_file:
            output_file.write(txt)

# merge_files(gold='/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/testing_gold_standards', output='/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/testing_full_text')

# Use our Pre-process for the gold standard files
def process_files(output_path):
    for file in os.listdir(output_dir_full_path):
        with open(os.path.join(output_dir_full_path, file), mode='r') as gold_file:
            gold = gold_file.read()
            txt = re_structure_text(gold)
            create_txt_file(txt, file, path=output_path)

# process_files(gold_pre_process_full_dir_path)

# region <! ------------- Sections Evaluation --------------- !>
# Section eval
output_dir_section_full_path = '/home/tzvi/PycharmProjects/HSdataprocessLinux/output/final_stage'
gold_pre_process_section_dir_path = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/pre_process_sections_'


# Use our Pre-process for the gold standard files
def process_section_files(output_path):
    sections_names = {
        0: 'other',
        1: 'chairmans_statement',
        2: 'chief_executive_officer_ceo_review',
        3: 'governance_statement',
        4: 'remuneration_report',
        5: 'business_review',
        6: 'financial_review',
        7: 'operating_review',
        8: 'highlights',
        9: 'auditors_report',
        10: 'risk_management',
        11: 'chairmans_governance_introduction',
        12: 'corporate_social_responsibility_csr_disclosures',
        13: 'chief_executive_officer_ceo_report'
    }
    for file in os.listdir(output_path):
        sec_id = file.split('_')[1][:-4]
        new_sec_name = sections_names[int(sec_id)]
        with open(os.path.join(output_path, file), mode='r') as gold_file:
            gold = gold_file.read()
            txt = re_structure_text(gold)
            file_name = '_'.join([file.split('_')[0], file.split('_')[1].replace(sec_id, new_sec_name)])
            create_txt_file(txt, file_name, path=gold_pre_process_section_dir_path)
            if sec_id == '2':  # If section is 2 create a copy with name tag of 13
                create_txt_file(txt, '_'.join([file.split('_')[0], file.split('_')[1].replace(sec_id, sections_names[13])]), path=gold_pre_process_section_dir_path)

# process_section_files(gold_standard_full_dir_path)
# endregion

import os
import pandas as pd
import pickle

def get_text_length(file_id, section_name):
    discourse_input_folder = '/home/tzvi/PycharmProjects/linuxDiscourse/src/Input/xmlParse'
    with open(os.path.join(os.path.join(discourse_input_folder, file_id), (file_id + '_' + '_'.join(section_name.split(' ')) + '.txt')), 'r') as eval_file:
        txt = eval_file.read()
        return len(txt)

# Original data ids
data_path = 'data'
ids = os.listdir(data_path)
ids = [file_id[:-4] for file_id in ids]
print(ids)

# Original data after pre-processing length
try:
    with open('proc_list1.pickle', 'rb') as q_list:
        queue = pickle.load(q_list)
    text_xml_path = '/home/tzvi/PycharmProjects/HSdataprocessLinux/output/text_xml'
    original_text_length = list()
    for file in queue:
        with open(os.path.join(text_xml_path, file), 'r') as xml_file:
            txt = xml_file.read()
            original_text_length.append((file, str(len(txt))))
    len_df = pd.DataFrame(original_text_length, columns=['file', 'file_length'])
    len_df.to_excel('file_length.xlsx', index=False)
except FileNotFoundError as e:
    print(e)

# Discourse processed files
discourse_output_folder = '/home/tzvi/PycharmProjects/linuxDiscourse/src/Output'
output_files = os.listdir(discourse_output_folder)
print(output_files)
eval_output = list()
for out_file in output_files:
    if out_file == 'Nucleus':
        continue
    out_file = out_file[:-4]
    cur_id = out_file.split('_')[0]
    fail_id = 0  # 0 - success; 1 - FAILED_SEG; 2 - FAILED_PARSE
    if 'FAILED_SEG' in out_file:  # 1
        fail_id = 1
        out_file = out_file.replace('_strip_output_', '_')
        out_file = out_file.replace('_output_', '_')
        out_file = out_file.replace('_FAILED_SEG', '')
        out_file = out_file.split('_')[1:]
        section_name = ' '.join(out_file)
        txt_len = get_text_length(cur_id, section_name)
        cur_tup = (cur_id, section_name, fail_id, txt_len)
        if cur_tup not in eval_output:
            eval_output.append(cur_tup)
    elif 'FAILED_PARSE' in out_file:  # 2
        fail_id = 2
        out_file = out_file.replace('_strip_output_', '_')
        out_file = out_file.replace('_output_', '_')
        out_file = out_file.replace('_FAILED_PARSE', '')
        out_file = out_file.split('_')[1:]
        section_name = ' '.join(out_file)
        txt_len = get_text_length(cur_id, section_name)
        cur_tup = (cur_id, section_name, fail_id, txt_len)
        if cur_tup not in eval_output:
            eval_output.append(cur_tup)
    else:
        out_file = out_file.replace('_strip_output', '')
        out_file = out_file.replace('_output', '')
        out_file = out_file.split('_')[1:]
        section_name = ' '.join(out_file)
        txt_len = get_text_length(cur_id, section_name)
        cur_tup = (cur_id, section_name, fail_id, txt_len)
        if cur_tup not in eval_output:
            eval_output.append(cur_tup)

df = pd.DataFrame(eval_output, columns=['file_id', 'section_name', 'status', 'text_length'])
print(df.head())
# Export to excel
df.to_excel('seg_parse_eval.xlsx', index=False)


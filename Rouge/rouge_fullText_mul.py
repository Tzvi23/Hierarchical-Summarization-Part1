from rouge import Rouge
import os
import pandas as pd


def rouge_score(hyp, ref):
    rouge = Rouge(return_lengths=True)
    scores = rouge.get_scores(hyp, ref)
    return scores[0]

def rouge_score_mul(hyp_list, ref_list):
    rouge = Rouge()
    scores = rouge.get_scores(hyp_list, ref_list, avg=True)
    return scores

# processed_files_dir = '/home/tzvi/PycharmProjects/HSdataprocessLinux/show_case/final_report/4/nucleus'
# gold_standard_files_dir = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/pre_process_text'

# processed_files_dir = '/home/administrator/HS_part1/HSdataprocessLinux/show_case/final_report/4/nucleus'
# gold_standard_files_dir = '/home/administrator/HS_part1/HSdataprocessLinux/gold_standard/pre_process_text'

processed_files_dir = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/MUSE_POLY/summaries_MUSE'
gold_standard_files_dir = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/testing_gold_standards'

r1_score = dict()
r2_score = dict()
rl_score = dict()

# Create dict with summary id and related gold standard
summary_dict = dict()
for file in os.listdir(processed_files_dir):
    summary_dict[file] = list()
for file in os.listdir(gold_standard_files_dir):
    file_name = file.split('_')[0] + '_summ.txt'
    summary_dict[file_name].append(file)

# Loop results
for file_id in summary_dict.keys():
    print(file_id)
    with open(os.path.join(processed_files_dir, file_id), 'r') as read_file:
        hypothesis = read_file.read().replace('\n', '').strip()
    hyp_list = [hypothesis for i in range(len(summary_dict[file_id]))]

    ref_list = list()
    for file_name in summary_dict[file_id]:
        with open(os.path.join(gold_standard_files_dir, file_name), 'r') as read_file:
            ref_list.append(read_file.read().replace('\n', ''))

    score = rouge_score_mul(hyp_list=hyp_list, ref_list=ref_list)

    r1_score[file_id] = score['rouge-1']

    r2_score[file_id] = score['rouge-2']

    rl_score[file_id] = score['rouge-l']


r1_df = pd.DataFrame.from_dict(r1_score, orient='index')
r1_df.loc['avg'] = r1_df.mean()
r2_df = pd.DataFrame.from_dict(r2_score, orient='index')
r2_df.loc['avg'] = r2_df.mean()
rl_df = pd.DataFrame.from_dict(rl_score, orient='index')
rl_df.loc['avg'] = rl_df.mean()

print(r1_df.head())
print(r2_df.head())
print(rl_df.head())

# Output files
with pd.ExcelWriter(os.path.join('rouge_output', 'rouge_full_text_MUSE_2.xlsx')) as writer:
    r1_df.to_excel(writer, sheet_name='rouge_1')
    r2_df.to_excel(writer, sheet_name='rouge_2')
    rl_df.to_excel(writer, sheet_name='rouge_l')


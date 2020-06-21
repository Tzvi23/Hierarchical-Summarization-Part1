from rouge import Rouge
import os
import pandas as pd


def rouge_score(hyp, ref):
    rouge = Rouge(return_lengths=True)
    scores = rouge.get_scores(hyp, ref)
    return scores[0]

# processed_files_dir = '/home/tzvi/PycharmProjects/HSdataprocessLinux/show_case/final_report/4/nucleus'
# gold_standard_files_dir = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/pre_process_text'

# processed_files_dir = '/home/administrator/HS_part1/HSdataprocessLinux/show_case/final_report/4/nucleus'
# gold_standard_files_dir = '/home/administrator/HS_part1/HSdataprocessLinux/gold_standard/pre_process_text'

processed_files_dir = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/MUSE_POLY/summaries_POLY'
gold_standard_files_dir = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/testing_full_text'

r1_score = dict()
r2_score = dict()
rl_score = dict()

# counter = 0
for file in os.listdir(processed_files_dir):
    print(file)
    # if counter == 3:
    #     break
    file_id = file.split('_')[0]

    # Hypothesis
    with open(os.path.join(processed_files_dir, file), 'r') as read_file:
        hypothesis = read_file.read().replace('\n', '').strip()
    # Reference
    with open(os.path.join(gold_standard_files_dir, file_id + '.txt'), 'r') as read_file:
        reference = read_file.read().replace('\n', '')

    score = rouge_score(hypothesis, reference)

    r1_score[file_id] = score['rouge-1']
    r1_score[file_id]['hyp'] = score['lengths']['hyp']
    r1_score[file_id]['ref'] = score['lengths']['ref']

    r2_score[file_id] = score['rouge-2']
    r2_score[file_id]['hyp'] = score['lengths']['hyp']
    r2_score[file_id]['ref'] = score['lengths']['ref']

    rl_score[file_id] = score['rouge-l']
    rl_score[file_id]['hyp'] = score['lengths']['hyp']
    rl_score[file_id]['ref'] = score['lengths']['ref']

    # counter += 1

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
with pd.ExcelWriter(os.path.join('rouge_output', 'rouge_full_text_POLY.xlsx')) as writer:
    r1_df.to_excel(writer, sheet_name='rouge_1')
    r2_df.to_excel(writer, sheet_name='rouge_2')
    rl_df.to_excel(writer, sheet_name='rouge_l')


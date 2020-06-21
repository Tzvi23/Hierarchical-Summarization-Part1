import os
from rouge import Rouge
import csv
import pandas as pd

def rouge_score(hyp, ref):
    rouge = Rouge(return_lengths=True)
    scores = rouge.get_scores(hyp, ref)
    return scores[0]

# processed_final_stage_dir = '/home/tzvi/PycharmProjects/HSdataprocessLinux/output/final_stage'
# gold_standard_sections_dir = '/home/tzvi/PycharmProjects/HSdataprocessLinux/gold_standard/pre_process_sections_text'

processed_final_stage_dir = '/home/administrator/HS_part1/HSdataprocessLinux/output/final_stage'
gold_standard_sections_dir = '/home/administrator/HS_part1/HSdataprocessLinux/gold_standard/pre_process_sections_text'

def eval_sections(final_stage_dir, gold_standard_dir, model_number):
    r1_score = dict()
    r2_score = dict()
    rl_score = dict()

    final_stage_dir = os.path.join(final_stage_dir, str(model_number))
    for file in os.listdir(gold_standard_dir):
        file_name = file[:-4]
        file_id = file.split('_')[0]
        file_dir = os.path.join(final_stage_dir, file_id)
        if not os.path.exists(file_dir):
            print(f'{file_id} directory not exists. Skip!')
            continue
        # Hypothesis - csv file
        if not os.path.exists(os.path.join(file_dir, file[:-4] + '_strip_output_processed.csv')):
            # Reference
            with open(os.path.join(gold_standard_dir, file[:-4] + '.txt'), 'r') as read_file:
                reference = len(read_file.read().replace('\n', ''))

            r1_score[file_name] = {'f': 0, 'p': 0, 'r': 0}
            r1_score[file_name]['hyp'] = 0
            r1_score[file_name]['ref'] = reference

            r2_score[file_name] = {'f': 0, 'p': 0, 'r': 0}
            r2_score[file_name]['hyp'] = 0
            r2_score[file_name]['ref'] = reference

            rl_score[file_name] = {'f': 0, 'p': 0, 'r': 0}
            rl_score[file_name]['hyp'] = 0
            rl_score[file_name]['ref'] = reference

            print(f'{file_name} => file not exists. Skip!')
        else:
            with open(os.path.join(file_dir, file[:-4] + '_strip_output_processed.csv'), 'r') as read_file:
                hypothesis = ''
                csv_reader = csv.DictReader(read_file)
                for row in csv_reader:
                    hypothesis += row['Nucleus_text']
            # Reference
            with open(os.path.join(gold_standard_dir, file[:-4] + '.txt'), 'r') as read_file:
                reference = read_file.read().replace('\n', '')

            if not reference:
                hyp = len(hypothesis)
                reference = len(reference)
                r1_score[file_name] = {'f': 0, 'p': 0, 'r': 0}
                r1_score[file_name]['hyp'] = hyp
                r1_score[file_name]['ref'] = reference

                r2_score[file_name] = {'f': 0, 'p': 0, 'r': 0}
                r2_score[file_name]['hyp'] = hyp
                r2_score[file_name]['ref'] = reference

                rl_score[file_name] = {'f': 0, 'p': 0, 'r': 0}
                rl_score[file_name]['hyp'] = hyp
                rl_score[file_name]['ref'] = reference

                continue

            score = rouge_score(hypothesis, reference)

            r1_score[file_name] = score['rouge-1']
            r1_score[file_name]['hyp'] = score['lengths']['hyp']
            r1_score[file_name]['ref'] = score['lengths']['ref']

            r2_score[file_name] = score['rouge-2']
            r2_score[file_name]['hyp'] = score['lengths']['hyp']
            r2_score[file_name]['ref'] = score['lengths']['ref']

            rl_score[file_name] = score['rouge-l']
            rl_score[file_name]['hyp'] = score['lengths']['hyp']
            rl_score[file_name]['ref'] = score['lengths']['ref']

    r1_df = pd.DataFrame.from_dict(r1_score, orient='index')
    r1_df.loc['avg'] = r1_df.mean()
    r2_df = pd.DataFrame.from_dict(r2_score, orient='index')
    r2_df.loc['avg'] = r2_df.mean()
    rl_df = pd.DataFrame.from_dict(rl_score, orient='index')
    rl_df.loc['avg'] = rl_df.mean()

    return r1_df, r2_df, rl_df


rouge1_df, rouge2_df, rougeL_df = eval_sections(processed_final_stage_dir, gold_standard_sections_dir, 4)
print(rouge1_df.head())
print(rouge2_df.head())
print(rougeL_df.head())

# Output to file
with pd.ExcelWriter(os.path.join('rouge_output', 'rouge_section_full_file.xlsx')) as writer:
    rouge1_df.to_excel(writer, sheet_name='rouge_1')
    rouge2_df.to_excel(writer, sheet_name='rouge_2')
    rougeL_df.to_excel(writer, sheet_name='rouge_l')

non_zero_rouge1_df, non_zero_rouge2_df, non_zero_rougeL_df = rouge1_df[rouge1_df['f'] != 0], rouge2_df[rouge2_df['f'] != 0], rougeL_df[rougeL_df['f'] != 0]
print(non_zero_rouge1_df.head())
print(non_zero_rouge2_df.head())
print(non_zero_rougeL_df.head())

# Output to file
with pd.ExcelWriter(os.path.join('rouge_output', 'rouge_section_non_zero.xlsx')) as writer:
    non_zero_rouge1_df.to_excel(writer, sheet_name='rouge_1')
    non_zero_rouge2_df.to_excel(writer, sheet_name='rouge_2')
    non_zero_rougeL_df.to_excel(writer, sheet_name='rouge_l')

# from __future__ import annotations
# from typing import Optional, Tuple
# from dataclasses import dataclass, fields
# from enum import Enum
# import re 
# import sys 

# INFILE = '/home/grace/work/brainmets/SEER/BrainMetsQueryFullSample.txt'
# OUTFILE = '/home/grace/work/brainmets/SEER/BrainMetsQueryFullSampleFmt.tsv'

# def main() -> None:
#     bm_df = pd.DataFrame(columns=TARGET_FIELDS)     # patients with brain met
#     mal_df = pd.DataFrame(columns=TARGET_FIELDS)    # patients with malignant tumors; no brain met
#     ben_df = pd.DataFrame(columns=TARGET_FIELDS)    # patients with benign tumors; no brain met
    
#     last_bm_idx = 0
#     paired_mal_queue = []
#     paired_ben_queue = []
#     with open(INFILE, 'r') as fp:
#         line = fp.readline()
#         prev_rec = gen_row(line)
#         line = fp.readline()
#         while line:
#             if last_bm_idx % 100000 == 0:
#                 print(f'Processed {last_bm_idx//100000} records', end='\r')
#             curr_rec = gen_row(line)

#             # patient same as last record - select & update better record
#             if curr_rec['patient_id'] == prev_rec['patient_id']:
#                 if should_replace_row(prev_rec, curr_rec):
#                     curr_rec = update_row(curr_rec, prev_rec)
#                 else:
#                     curr_rec = update_row(prev_rec, curr_rec)
            
#             # patient different to last record
#             # update brain met dataframe
#             elif prev_rec['patient_behavior'] == Behavior.BRAIN_MET:
#                 prev_rec['bm_id'] = last_bm_idx
#                 bm_df.loc[last_bm_idx] = pd.Series(prev_rec)
#                 paired_mal_queue.append((prev_rec['bm_id'], prev_rec['site']))
#                 paired_ben_queue.append((prev_rec['bm_id'], prev_rec['site']))
#                 last_bm_idx += 1

#             # update malignant dataframe
#             elif prev_rec['patient_behavior'] == Behavior.MALIGNANT:
#                 for i, (idx, site) in enumerate(paired_mal_queue):
#                     if prev_rec['site'] == site:
#                         prev_rec['bm_id'] = idx
#                         mal_df.loc[idx] = pd.Series(prev_rec)
#                         break 
#                     del paired_mal_queue[i]
            
#             # update benign dataframe
#             elif prev_rec['patient_behavior'] in [Behavior.BENIGN, Behavior.BORDERLINE]:
#                 for i, (idx, site) in enumerate(paired_ben_queue):
#                     if prev_rec['site'] == site:
#                         prev_rec['bm_id'] = idx
#                         ben_df.loc[idx] = pd.Series(prev_rec)
#                         break 
#                     del paired_ben_queue[i]
            
#             # boundary
#             else:
#                 raise RuntimeError

#             # continue to next record 
#             prev_rec = curr_rec
#             line = fp.readline()

#     bm_df.to_csv(OUTFILE_BM, sep='\t', header=True, index=False)
#     mal_df.sort_values(by='bm_id')
#     ben_df.sort_values(by='bm_id')
#     mal_df.to_csv(OUTFILE_MAL, sep='\t', header=True, index=False)
#     ben_df.to_csv(OUTFILE_BEN, sep='\t', header=True, index=False)



# SHITTY_SITES = ['NHL - Extranodal', 'NHL - Nodal', 'Miscellaneous']

# def should_replace_rec(target: Record, incoming: Record) -> bool:
#     if incoming.behavior.value > target.behavior.value:
#         return True
#     elif incoming.site not in SHITTY_SITES and target.site in SHITTY_SITES:
#         return True
#     elif incoming.grade_std.value > incoming.grade_std.value:
#         return True
#     elif incoming.diagnosis_year > incoming.diagnosis_year:
#         return True
#     return False

# def update_rec(target: Record, incoming: Record) -> Record:
#     target['patient_num_malignant_tumors'] = max(target['patient_num_malignant_tumors'], incoming['patient_num_malignant_tumors'])
#     target['patient_num_benign_tumors'] = max(target['patient_num_benign_tumors'], incoming['patient_num_benign_tumors'])
#     if target['patient_death_year'] is None:
#         target['patient_death_year'] = incoming['patient_death_year']
#     return target

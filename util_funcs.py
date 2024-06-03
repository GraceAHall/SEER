

import pandas as pd
from collections import defaultdict

from util_classes import Patient, Record
from util_consts import ISEP_CHAR
import re 
import numpy as np





def get_last(cell: str) -> str:
    return cell.split(ISEP_CHAR)[-1]

# flatlist = lambda x, y: x + y.split('|')

def get_total_counts(df: pd.DataFrame, field: str) -> dict[str, int]:
    singles = df.loc[df['num_records'] == 1]
    multiples = df.loc[df['num_records'] > 1]
    counts = dict(singles[field].value_counts())
    multi_list = multiples[field].tolist()
    for item in multi_list:
        sites = item.split('|')
        for site in sites:
            if site not in counts:
                counts[site] = 0
            counts[site] += 1
    return counts


def load_patients(filepath: str) -> pd.DataFrame:
    # TODO this is bad, use pandas instead. 
    data = defaultdict(dict)
    with open(filepath, 'r') as fp:
        # ignore header
        line = fp.readline() 

        # first line
        line = fp.readline()
        the_rec = Record.fromstr(line)
        active_patient = Patient(the_rec.patient_id)
        active_patient.update(the_rec)

        processed = 1
        line = fp.readline()
        while line:
            if processed % 100000 == 0:
                print(f'Processed {processed} records', end='\r')
            
            the_rec = Record.fromstr(line)
            if the_rec.patient_id == active_patient.patient_id:
                active_patient.update(the_rec)
            else:
                data[active_patient.patient_id] = active_patient.todict()
                active_patient = Patient(the_rec.patient_id)
                active_patient.update(the_rec)

            line = fp.readline()
            processed += 1
            
        data[active_patient.patient_id] = active_patient.todict()

    master = pd.DataFrame.from_dict(data, orient='index')
    del data
    return master
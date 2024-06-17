
import pandas as pd
from util_consts import ISEP_CHAR
import re 
import numpy as np

def do_basic_formatting(df: pd.DataFrame, histtypes_path: str) -> pd.DataFrame:
    # year ranges
    df = df.loc[df['diagnosis_year'] >= 2010]
    df = df.loc[df['diagnosis_year'] <= 2020]
    
    for field in ['brain_met', 'bone_met', 'lung_met', 'liver_met', 'distant_ln']:
        # reassign NA -> False for brain_met field
        df[field] = df[field].fillna(value=False)
        # bool to 'YES' 'NO'
        df[field] = df[field].apply(lambda x: 'YES' if x else 'NO')

    # removing codes from hist_category
    df['hist_cateogry'] = df['hist_cateogry'].apply(lambda x: x.split(':')[-1].strip())
    
    # reassign int -> string for hist_type field
    df['hist_type'] = df['hist_type'].apply(str)
    
    # histologic type: code to description. (mappings available in tsv file)
    the_map = {}
    with open(histtypes_path, 'r') as fp:
        line = fp.readline()
        while line:
            code, descr = line.strip('\n').split('\t')
            the_map[code] = descr
            line = fp.readline()

    seer_codes = list(df['hist_type'].unique())
    seer_codes = set([str(x) for x in seer_codes])
    known_codes = set(the_map.keys())
    missing_codes = seer_codes - known_codes
    print(f'Missing {len(missing_codes)} codes.')
    for code in missing_codes:
        print(code)

    def _map_histcode_to_descr(code: str) -> str:
        descr = the_map[code]
        if '|' in descr:
            descr = descr.split('|')[0] + ' [+ others]'
        return descr
 
    df['hist_type_descr'] = df['hist_type'].apply(_map_histcode_to_descr)
    return df 


TSTAGE_PATTERN = r'^(T[1234])'
NSTAGE_PATTERN = r'^(N[0123])'
GSTAGE_PATTERN = r'^(IV|III|II|I|0)'

def std_tstage(stage: str | float) -> str | float:
    """
    target: {T1, T2, T3, T4}
    T1a -> T1 etc
    ignore T0, TX, Ta, Tis, Tispd etc. 
    """
    if isinstance(stage, str):
        m = re.match(TSTAGE_PATTERN, stage)
        if m:
            return m.group(1)
    return np.nan

def std_nstage(stage: str | float) -> str | float:
    """
    target: {N0, N1, N2, N3}
    ignore NX
    N0: no detectable lymph nodes (ie no spread)
    """
    if isinstance(stage, str):
        m = re.match(NSTAGE_PATTERN, stage)
        if m:
            return m.group(1)
    return np.nan

def std_gstage(stage: str | float) -> str | float:
    """
    target: {N0, N1, N2, N3}
    ignore NX
    N0: no detectable lymph nodes (ie no spread)
    """
    if isinstance(stage, str):
        if stage == 'OCCULT':
            return np.nan
        m = re.match(GSTAGE_PATTERN, stage)
        assert m 
        return m.group(1)
    return np.nan

def std_grade(grade: str) -> str | float:
    if grade == 'NA':
        return np.nan 
    return grade 
    # if grade == 'G1':
    #     return 1
    # elif grade == 'G2':
    #     return 2
    # elif grade == 'G3':
    #     return 3
    # elif grade == 'G4':
    #     return 4
    # else:
    #     return np.nan


def filter_for_incidence(df: pd.DataFrame) -> pd.DataFrame:
    DISPLAY_FIELDS = ['patient_id', 'cancer_type', 'diagnosis_year', 'patient_death_year', 'brain_met']
    filterfuncs = [
        (_filter_multirecords, 'keep patients with 2+ records'),
        (_filter_noinitialbm, 'remove patients with brain met on first contact'),
        (_filter_postbm, 'remove records after brain met detected'),
        (_filter_years, 'keep patients with 2+ diagnosis_years on record'),
    ]
    for func, descr in filterfuncs:
        print(f'\n\n--- Filtering: {descr} ---\n'.upper())
        i_records = df.shape[0]
        i_pats = df['patient_id'].unique()
        df = func(df)
        f_records = df.shape[0]
        f_pats = df['patient_id'].unique()
        f_bm_pats = set(df[df['brain_met']=='YES']['patient_id'].unique())
        print(f'Removed: {len(i_pats) - len(f_pats)} patients, {i_records - f_records} records')
        print(f'Remaining [Yes Brain Met]: {len(f_bm_pats)} patients')
        print(f'Remaining [Non Brain Met]: {len(f_pats) - len(f_bm_pats)} patients')
        print('\nTable peek (no bm):')
        print(df[~df['patient_id'].isin(f_bm_pats)][DISPLAY_FIELDS].head())
        print('\nTable peek (yes bm):')
        print(df[df['patient_id'].isin(f_bm_pats)][DISPLAY_FIELDS].head())
    return df 

def _filter_multirecords(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df.duplicated(subset=['patient_id'], keep=False)]
    df.reset_index(drop=True, inplace=True)
    return df

def _filter_years(df: pd.DataFrame) -> pd.DataFrame:
    pids = df.groupby('patient_id', as_index=False)['diagnosis_year'].nunique()
    pids = pids[pids['diagnosis_year'] >= 2]
    keep_pids = pids['patient_id'].unique()
    df = df[df['patient_id'].isin(keep_pids)]
    df.reset_index(drop=True, inplace=True)
    return df 

def _filter_noinitialbm(df: pd.DataFrame) -> pd.DataFrame:
    # sort by brain_met->year->pid so that first record will be earliest. 
    # if multiple records at first timepoint, if 1+ are marked brain met positive, these records will be the first.
    df.sort_values(by=['patient_id', 'diagnosis_year', 'brain_met'], ascending=[True, True, False], ignore_index=True)

    # select first record for each patient
    first_records = df.drop_duplicates(subset=['patient_id'], keep='first', ignore_index=True)

    # identify pids to keep (first record can't include brain met)
    keep_pids = set(first_records[first_records['brain_met']=='NO']['patient_id'].unique())

    # do subsetting
    df = df[df['patient_id'].isin(keep_pids)]
    return df

def _filter_postbm(df: pd.DataFrame) -> pd.DataFrame:
    bm_df = df[df['brain_met']=='YES'][['patient_id', 'diagnosis_year']]
    the_dict = bm_df.groupby('patient_id')['diagnosis_year'].apply(min).to_dict()

    def _is_after_bm(pid: int, year: int, has_bm: bool) -> bool:
        if pid in the_dict:
            if year > the_dict[pid]:
                return True
            elif year == the_dict[pid] and not has_bm:
                return True 
        return False

    bool_vector = df.apply(lambda x: _is_after_bm(x.patient_id, x.diagnosis_year, x.brain_met), axis=1)
    df = df[~bool_vector]
    return df

def format_for_incidence(df: pd.DataFrame) -> pd.DataFrame:
    # very slow, unsure why.
    print('calculating dictionaries. this may take a while.')
    brainmet_df = df[df['brain_met']=='YES'][['patient_id', 'diagnosis_year']]
    brainmet_dict = brainmet_df.groupby('patient_id')['diagnosis_year'].apply(min).to_dict()
    deathyear_df = df.dropna(subset=['patient_death_year'])[['patient_id', 'patient_death_year']]
    deathyear_dict = deathyear_df.groupby('patient_id')['patient_death_year'].apply(max).to_dict()
    lastcontact_dict = df.groupby('patient_id')['diagnosis_year'].apply(max).to_dict()

    # very slow, unsure why.
    print('calculating second timepoints. this may take a while.')
    def _calc_timepoint2_info(pid: int) -> pd.Series:
        if pid in brainmet_dict:
            tp2 = brainmet_dict[pid]
            obs = True
        elif pid in deathyear_dict:
            tp2 = deathyear_dict[pid]
            obs = False
        else:
            tp2 = lastcontact_dict[pid]
            obs = False
        return pd.Series([tp2, obs])
    
    df[['timepoint2', 'observed']] = df['patient_id'].apply(_calc_timepoint2_info)
    return df

def finalise_incidence_df(df: pd.DataFrame) -> pd.DataFrame:
    i_records = df.shape[0]
    i_pats = df['patient_id'].unique()
    # float to int
    df['timepoint2'] = df['timepoint2'].apply(int)
    
    # remove entries where diagnosis_year == timepoint2
    df = df[df['diagnosis_year'] < df['timepoint2']]

    # remove brain_met field
    df = df.drop('brain_met', axis=1)
    
    f_records = df.shape[0]
    f_pats = df['patient_id'].unique()
    print(f'Removed: {len(i_pats) - len(f_pats)} patients, {i_records - f_records} records')
    return df

def get_last(cell: str) -> str:
    return cell.split(ISEP_CHAR)[-1]

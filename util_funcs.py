
from typing import Optional
from typing import Tuple

import pandas as pd
from util_consts import ISEP_CHAR
from util_classes import Settings
import re 
import numpy as np
from scipy.stats.contingency import odds_ratio


def format_cancer_subtypes(df: pd.DataFrame) -> pd.DataFrame:

    def _format_appendix_subtype(hist: str) -> str:
        hist = hist.lower()
        if 'carcinoid' in hist.lower():
            return 'Appendix (carcinoid)'
        return 'Appendix (carcinoma)'
    
    def _format_corpus_uteri_subtype(hist: str) -> str:
        hist = hist.lower()
        if 'carcinosarcoma' in hist:
            return 'Corpus Uteri (carcinoma)'
        if 'sarcoma' in hist:
            return 'Corpus Uteri (sarcoma)'
        return 'Corpus Uteri (carcinoma)'

    for field in ['cancer_type', 'cancer_group']:
        ### APPENDIX ###
        mask = df[field] == 'Appendix'
        df.loc[mask, field] = df.loc[mask, 'hist_type_descr'].apply(_format_appendix_subtype)
        
        ### CORPUS UTERI ###
        mask = df[field] == 'Corpus Uteri'
        df.loc[mask, field] = df.loc[mask, 'hist_type_descr'].apply(_format_corpus_uteri_subtype)
    
    return df 


def do_basic_filtering(df: pd.DataFrame) -> pd.DataFrame:
    print('Removing records not in range (2010, 2020)')
    irecords = df.shape[0]
    df = df.loc[df['diagnosis_year'] >= 2010]
    df = df.loc[df['diagnosis_year'] <= 2020]
    print(f'- removed {irecords - df.shape[0]} records')
    
    print('Selecting records with MALIGNANT behavior')
    irecords = df.shape[0]
    df = df[df['behavior']=='MALIGNANT']
    print(f'- removed {irecords - df.shape[0]} records')

    print('Handling patients with multiple records of same cancer_type')
    irecords = df.shape[0]
    # df = df[~df.duplicated(subset=['patient_id', 'cancer_type', 'hist_cateogry'])]
    df = df[~df.duplicated(subset=['patient_id', 'cancer_type'])]
    print(f'- removed {irecords - df.shape[0]} records')
    
    print('Removing records where any met value (except distant LN) is missing')
    irecords = df.shape[0]
    MET_FIELDS = ['brain_met', 'bone_met', 'lung_met', 'liver_met']
    df = df.dropna(subset=MET_FIELDS)
    print(f'- removed {irecords - df.shape[0]} records')

    print(f'\nFinal records: {df.shape[0]}, patients: {len(df.patient_id.unique())}')
    return df


def do_basic_formatting(df: pd.DataFrame, histtypes_path: str) -> pd.DataFrame:
    # mets: any_met
    MET_FIELDS = ['brain_met', 'bone_met', 'lung_met', 'liver_met']
    df['any_met'] = df[MET_FIELDS].any(axis=1)
    
    # mets: bool to 'YES' 'NO'
    for field in MET_FIELDS + ['any_met']:
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

    print('Formatting cancer subtypes')
    df = format_cancer_subtypes(df)

    print('TNG, Grade standardisation')
    df['TSTAGE_STD'] = df['t_stage_ajcc'].apply(std_tstage)
    df['NSTAGE_STD'] = df['n_stage_ajcc'].apply(std_nstage)
    df['GSTAGE_STD'] = df['g_stage_ajcc'].apply(std_gstage)
    df['GRADE_STD'] = df['grade'].apply(std_grade)

    return df 


def normalize_field_pergroup(
    groups: str, 
    target_field: str, 
    norm_field: str,
    norm_meth: str,
    df: pd.DataFrame
    ) -> pd.DataFrame:
    df[norm_field] = 0
    for gval in df[groups].unique():
        temp = df[df[groups]==gval]

        # method 1: normalise values to range 0-1
        if norm_meth == 'range':
            temp[norm_field] = (temp[target_field] - temp[target_field].min()) / (temp[target_field].max() - temp[target_field].min()) 

        # method2: normalise values as percentage of max 
        elif norm_meth == 'max':
            temp[norm_field] = temp[target_field] / temp[target_field].max() 
        
        # method3: normalise values as proportion of total
        elif norm_meth == 'sum':
            temp[norm_field] = temp[target_field] / temp[target_field].sum() 
        
        else:
            raise ValueError
        
        df.loc[df[groups]==gval, norm_field] = temp[norm_field]
    df[norm_field] = df[norm_field].fillna(value=0)
    return df


def calculate_met_stats(
    feature: str, 
    response: str, 
    df: pd.DataFrame,
    cohort_yes: Optional[float]=None,
    cohort_no: Optional[float]=None,
    baseline_fval: Optional[str]=None
    ) -> pd.DataFrame: 
    yn_df = df.groupby(by=[feature, response]).size().unstack(fill_value=0)
    prevs = yn_df.reset_index()
    if 'YES' not in prevs.columns:
        prevs['YES'] = 0
    if 'NO' not in prevs.columns:
        prevs['NO'] = 0
    prevs['records'] = prevs['YES'] + prevs['NO']
    prevs['prevalence (%)'] = (prevs['YES'] / (prevs['YES'] + prevs['NO'])) * 100
    prevs = prevs.set_index(feature, drop=True)

    if cohort_yes is not None and cohort_no is not None:
        odds_stats = pd.DataFrame(index=prevs.index, columns=['OR_STAT', 'OR_CI_LOW', 'OR_CI_HIGH'])

        for i, fval in enumerate(df[feature].unique()):
            cont = pd.DataFrame(columns=['subset', 'reference'], index=['YES', 'NO'], data=[[0, 0],[0, 0]])
            cont.loc['YES', 'reference'] = cohort_yes
            cont.loc['YES', 'subset'] = prevs.loc[fval, 'YES']
            cont.loc['NO', 'reference'] = cohort_no
            cont.loc['NO', 'subset'] = prevs.loc[fval, 'NO']
            res = odds_ratio(cont, kind='sample')
            ci = res.confidence_interval(confidence_level=0.95)
            odds_stats.loc[fval] = pd.Series({'OR_STAT': res.statistic, 'OR_CI_LOW': ci.low, 'OR_CI_HIGH': ci.high})
        
        prevs = prevs.join(odds_stats)

    elif baseline_fval is not None:
        odds_stats = pd.DataFrame(index=prevs.index, columns=['OR_STAT', 'OR_CI_LOW', 'OR_CI_HIGH'])
        baseline_yes = prevs.loc[baseline_fval, 'YES']
        baseline_no = prevs.loc[baseline_fval, 'NO']
        for i, fval in enumerate(df[feature].unique()):
            if fval == baseline_fval:
                odds_stats.loc[fval] = pd.Series({'OR_STAT': 1, 'OR_CI_LOW': 1, 'OR_CI_HIGH': 1})
                continue 

            cont = pd.DataFrame(columns=['subset', 'reference'], index=['YES', 'NO'], data=[[0, 0],[0, 0]])
            cont.loc['YES', 'reference'] = baseline_yes
            cont.loc['YES', 'subset'] = prevs.loc[fval, 'YES']
            cont.loc['NO', 'reference'] = baseline_no
            cont.loc['NO', 'subset'] = prevs.loc[fval, 'NO']
            res = odds_ratio(cont, kind='sample')
            ci = res.confidence_interval(confidence_level=0.95)
            odds_stats.loc[fval] = pd.Series({'OR_STAT': res.statistic, 'OR_CI_LOW': ci.low, 'OR_CI_HIGH': ci.high})
        
        prevs = prevs.join(odds_stats)

    return prevs


def calculate_bm_prevalence_grouped(
    groups: list[str],
    features: list[str], 
    response_field: str,
    s: Settings,
    df: pd.DataFrame, 
    groups_subset: Optional[dict]=None, 
    features_subset: Optional[dict]=None
    ) -> pd.DataFrame:
    # remove records where there is no value for any of the features.
    # 
    # eg if features == ['t_stage_ajcc', 'n_stage_ajcc']:
    # patient_id	cancer_type	t_stage_ajcc	n_stage_ajcc
    # 137	        Myeloma	    NaN	            NaN     <- remove
    # 139	        Breast	    T3	            N0
    # 142	        Breast	    T2	            N1
    # 194	        Ovary	    NaN	            N1      <- remove

    # print('dropping missing feature values')
    temp = df.dropna(subset=features)  
    # print('dropping missing group values')
    temp = temp.dropna(subset=groups)  
    
    if groups_subset is not None:
        for gname, gvals in groups_subset.items():
            temp = temp[temp[gname].isin(gvals)]
    if features_subset is not None:
        for fname, fvals in features_subset.items():
            if fname in features:
                temp = temp[temp[fname].isin(fvals)]

    for feat in features:
        if str(temp.dtypes[feat]) != 'object':
            # print(f'mapping {feat} to str categorical variable')
            temp[feat] = temp[feat].apply(str)

    # # init variables
    # print(f'creating compound groups using {groups}')
    if len(groups) == 1:
        temp[s.COMPOUND_GROUP] = temp[groups[0]]
    else:
        temp[s.COMPOUND_GROUP] = temp[groups].agg(':'.join, axis=1)
    
    # # init variables
    # print(f'creating compound features using {features}')
    if len(features) == 1:
        temp[s.COMPOUND_FEATURE] = temp[features[0]]
    else:
        temp[s.COMPOUND_FEATURE] = temp[features].agg(':'.join, axis=1)

    # FILTERING: remove groups with too few records. 
    # dropping na above will reduce num records for each group. 
    # eg if groups == 'cancer_type', might remove 'Placenta' because there's not many records for this type.
    # print(f'prelim (efficiency) filtering for {groups} members with too few records')
    temp = temp.groupby(s.COMPOUND_GROUP).filter(lambda x: len(x) > s.THRESH_RECORDS)
    
    # members = list(temp[s.COMPOUND_FEATURE].unique())
    # PRINTFIELDS = ['patient_id', 'cancer_type'] + features + [s.COMPOUND_FEATURE]
    # print(temp[PRINTFIELDS].head())
    # print('\ncompound feature members:')
    # for i in range(0, len(members), 5):
    #     print('\t'.join(members[i:i + 5]))

    # init variables
    i = 0
    maintable = pd.DataFrame()
    groupvals = temp[s.COMPOUND_GROUP].unique()
    
    filtered = []
    # iter through each subdivision
    for gval in groupvals:
        i += 1
        temp_group = temp[temp[s.COMPOUND_GROUP]==gval][[s.COMPOUND_FEATURE, response_field]]
        sprev = calculate_met_stats(
            feature=s.COMPOUND_FEATURE, 
            response=response_field, 
            df=temp_group
        )
        num_failing_rec_thresh = sum(sprev['records'] < s.THRESH_RECORDS)
        num_failing_yes_thresh = sum(sprev['YES'] < s.THRESH_POSITIVE)
        nfeatures = sprev.shape[0]
        
        # print(sprev)
        # print(f'\nfailing records: {num_failing_rec_thresh}')
        # print(f'failing bm cases: {num_failing_yes_thresh}')
        # print(f'num features: {nfeatures}')
        
        # filter condition 1: 50% or greater features must have >thresh records. 
        if num_failing_rec_thresh / nfeatures > 0.5:
            filtered.append(gval)
            continue 
        # filter condition 2: 50% or greater features must have >thresh bm cases. 
        if num_failing_yes_thresh / nfeatures > 0.5:
            filtered.append(gval)
            continue 
        
        sprev = sprev.reset_index()
        sprev[s.COMPOUND_GROUP] = gval
        maintable = pd.concat([maintable, sprev], ignore_index=True)
        print(f'{i}/{len(groupvals)} subsets calculated', end='\r')

    print(f'\nRemoved {len(filtered)}/{len(groupvals)} groups:')
    for gval in filtered:
        print(f'-{gval}')

    return maintable



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

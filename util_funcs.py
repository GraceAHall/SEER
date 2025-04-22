
from typing import Optional, Tuple

import pandas as pd
from util_consts import ISEP_CHAR
import settings as s
import re 
import numpy as np
import math
from scipy.stats.contingency import odds_ratio, relative_risk

import matplotlib.pyplot as plt
import seaborn as sns

HISTTYPES_PATH = '/home/grace/work/SEER/data/histology/histcodes.tsv'

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


def format_ln_status(df: pd.DataFrame, basis: str) -> pd.DataFrame:
    print('formatting ln_status')

    if basis == 'clinical':
        return _format_ln_status_clinical(df)
    elif basis == 'pathological':
        return _format_ln_status_pathological(df)
    else:
        raise ValueError

def _format_ln_status_clinical(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use pathological first (if available), then clinical. 
    """
    df = _format_ln_status_pathological(df)
    df.loc[(df['local_ln'].isna()) & (df['NSTAGE_STD']=='N0'), 'local_ln'] = False
    df.loc[(df['local_ln'].isna()) & (df['NSTAGE_STD'].isin(['N1', 'N2', 'N3'])), 'local_ln'] = True
    return df    
 
    # neither (not NA)
    df.loc[(df['regional_nodes_positive'] == 0) & (df['distant_ln'] == False), 'ln_status'] = 'negative'
    df.loc[(df['ln_status'].isna()) & (df['NSTAGE_STD']=='N0') & (df['distant_ln'] == False), 'ln_status'] = 'negative'

    # locoregional only
    df.loc[(df['regional_nodes_positive'] > 0) & (df['distant_ln'] == False), 'ln_status'] = 'positive local'
    df.loc[(df['ln_status'].isna()) & (df['NSTAGE_STD'].isin(['N1', 'N2', 'N3'])) & (df['distant_ln'] == False), 'ln_status'] = 'positive local'

    # distant only
    df.loc[(df['regional_nodes_positive'] == 0) & (df['distant_ln'] == True), 'ln_status'] = 'positive distant'
    df.loc[(df['ln_status'].isna()) & (df['NSTAGE_STD']=='N0') & (df['distant_ln'] == True), 'ln_status'] = 'positive distant'

    # both 
    df.loc[(df['regional_nodes_positive'] > 0) & (df['distant_ln'] == True), 'ln_status'] = 'positive local+distant'
    df.loc[(df['ln_status'].isna()) & (df['NSTAGE_STD'].isin(['N1', 'N2', 'N3'])) & (df['distant_ln'] == True), 'ln_status'] = 'positive local+distant'
    return df

def _format_ln_status_pathological(df: pd.DataFrame) -> pd.DataFrame:
    """
    use 'regional_nodes' field. 
        NEG:            False
        POS_NODES:      True
        POS_ASPIRATION: False
    """
    df['local_ln'] = np.nan
    df.loc[df['regional_nodes']=='NEG', 'local_ln'] = False
    df.loc[df['regional_nodes'].isin(['POS_NODES', 'POS_ASPIRATION']), 'local_ln'] = True
    return df

def format_regional_nodes_bins(df: pd.DataFrame) -> pd.DataFrame:
    print('formatting regional nodes derived fields')
    df['regional_nodes_prop'] = np.nan
    df['regnodes_exam_bin'] = np.nan
    df['regnodes_pos_bin'] = np.nan
    df['regnodes_prop_bin'] = np.nan

    # proportion
    mask = (df['regional_nodes_examined'] > 0) & (df['regional_nodes_positive'] >= 0)
    df.loc[mask, 'regional_nodes_prop'] = (df.loc[mask]['regional_nodes_positive'] / df.loc[mask]['regional_nodes_examined'])

    # num examined bin
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    mask = df['regional_nodes_examined'] >= 0
    df.loc[mask, 'regnodes_exam_bin'] = pd.cut(df['regional_nodes_examined'], bins, include_lowest=True).astype(str)
    df.loc[df['regnodes_exam_bin']=='(-0.001, 10.0]', 'regnodes_exam_bin'] = '(0, 10]'

    # num examined bin
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    mask = df['regional_nodes_positive'] >= 0
    df.loc[mask, 'regnodes_pos_bin'] = pd.cut(df['regional_nodes_positive'], bins, include_lowest=True).astype(str)
    df.loc[df['regnodes_pos_bin']=='(-0.001, 10.0]', 'regnodes_pos_bin'] = '(0, 10]'

    # proportion bin
    bins = [0.00, 0.25, 0.50, 0.75, 1.00]
    mask = df['regional_nodes_prop'] >= 0
    df.loc[mask, 'regnodes_prop_bin'] = pd.cut(df['regional_nodes_prop'], bins, include_lowest=True).astype(str)
    df.loc[df['regnodes_prop_bin']=='(-0.001, 0.25]', 'regnodes_prop_bin'] = '(0.00, 0.25]'
    return df 


def do_basic_filtering(df: pd.DataFrame, filter_mets: Optional[str]=None) -> pd.DataFrame:
    print(f"Reginning records: {df.shape[0]}")
    print('Removing records not in range (2010, 2020)...', end='\r')
    irecords = df.shape[0]
    df = df.loc[df['diagnosis_year'] >= 2010]
    df = df.loc[df['diagnosis_year'] <= 2020]
    print(f"Removing records not in range (2010, 2020)... removed {irecords - df.shape[0]} records")
    
    print("Removing records with non 'MALIGNANT' behavior...", end='\r')
    irecords = df.shape[0]
    df = df[df['behavior']=='MALIGNANT']
    print(f"Removing records with non 'MALIGNANT' behavior... removed {irecords - df.shape[0]} records")

    print('Handling patients with multiple records of same cancer_type...', end='\r')
    irecords = df.shape[0]
    # df = df[~df.duplicated(subset=['patient_id', 'cancer_type', 'hist_cateogry'])]
    df = df[~df.duplicated(subset=['patient_id', 'cancer_type'])]
    print(f"Handling patients with multiple records of same cancer_type... removed {irecords - df.shape[0]} records")
    
    if filter_mets == 'all':
        MET_FIELDS = ['brain_met', 'bone_met', 'lung_met', 'liver_met', 'other_met']
        print('Removing records where any of the following fields have missing values:')
        print(MET_FIELDS)
        irecords = df.shape[0]
        df = df.dropna(subset=MET_FIELDS)
        print(f'- removed {irecords - df.shape[0]} records')
    
    elif filter_mets == 'brain':
        print('Removing records where brain_met value is missing')
        irecords = df.shape[0]
        df = df.dropna(subset=['brain_met'])
        print(f'- removed {irecords - df.shape[0]} records')

    print(f'\nFinal records: {df.shape[0]}, patients: {len(df.patient_id.unique())}')
    return df

def select_valid(
    df: pd.DataFrame, 
    feature: str,  
    min_records: int=1000,
    sec_features: set[str]|None=None, 
    sec_mincount: int|None=None) -> set[str]:

    counts = pd.DataFrame(index=list(df[feature].unique()))
    counts['records'] = df.groupby(feature).size()

    if sec_features is not None:
        assert sec_mincount is not None
        for sfeat in sec_features:
            counts[sfeat] = df[df[sfeat]=='YES'].groupby(feature).size()
    
    counts = counts.fillna(0).astype(int)
    counts['valid'] = False
    
    for idx, row in counts.iterrows():
        if row['records'] >= min_records:
            if sec_features is None:
                counts.loc[idx, 'valid'] = True
            elif all([row[x]>=sec_mincount for x in sec_features]):
                counts.loc[idx, 'valid'] = True

    # print(counts)
    valid = set(counts[counts['valid']==True].index.to_list())
    if 'Miscellaneous' in valid:
        valid.remove('Miscellaneous')
    if 'unspecified neoplasms' in valid:
        valid.remove('unspecified neoplasms')
    return valid

def remove_identical_primary_secondary_cases(df: pd.DataFrame) -> pd.DataFrame:
    MET_MAP = {
        'brain_met': ['Brain'], 
        'bone_met': ['Bones and Joints'], 
        'lung_met': ['Lung and Bronchus'],
        'liver_met': ['Liver'], 
    }

    print('Removing MET records where primary tissue is identical to secondary tissue')
    irecords = df.shape[0]
    for met, tissues in MET_MAP.items():
        mask = (df[met]==True) & (df['cancer_type'].isin(tissues))
        df = df[~mask]
    print(f'- removed {irecords - df.shape[0]} records')
    return df  

def do_basic_formatting(df: pd.DataFrame) -> pd.DataFrame:
    # mets: any_met
    MET_FIELDS = ['brain_met', 'bone_met', 'lung_met', 'liver_met', 'other_met']
    df['any_met'] = df[MET_FIELDS].any(axis=1)
    
    # mets: bool to 'YES' 'NO'
    for field in MET_FIELDS + ['any_met']:
        the_map = {
            np.nan: np.nan,
            True: 'YES',
            False: 'NO'
        }
        df[field] = df[field].map(the_map)

    # histology:removing codes from hist_category
    df['hist_cateogry'] = df['hist_cateogry'].apply(lambda x: x.split(':')[-1].strip())
    
    # histology: reassign int -> string for hist_type field
    df['hist_type'] = df['hist_type'].apply(str)
    
    # histology: category to group
    def _format_hist_group(histtext: str) -> str:
        mapper = {
            'epithelial neoplasms, NOS': 'epithelial neoplasms',
            'complex epithelial neoplasms': 'epithelial neoplasms',
            'soft tissue tumors and sarcomas, NOS': 'soft tissue tumors and sarcomas',
        }
        return mapper.get(histtext, histtext)
    df['hist_group'] = df['hist_cateogry'].apply(_format_hist_group)

    # histology: code to description. (mappings available in tsv file)
    the_map = {}
    with open(HISTTYPES_PATH, 'r') as fp:
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

    # cancer subtypes
    print('Formatting cancer subtypes')
    df = format_cancer_subtypes(df)

    # categorical fields
    print('TNG, Grade standardisation')
    df['TSTAGE_STD'] = df['t_stage_ajcc'].apply(std_tstage)
    df['NSTAGE_STD'] = df['n_stage_ajcc'].apply(std_nstage)
    df['GSTAGE_STD'] = df['g_stage_ajcc'].apply(std_gstage)
    df['GRADE_STD'] = df['grade'].apply(std_grade)
    
    # remove records where Grade is 'T_CELL'
    df = df[~(df['GRADE_STD']=='T_CELL')]

    return df 

def format_nstage_twolevel(df: pd.DataFrame) -> pd.DataFrame:
    print('Mapping NSTAGE field to two levels: N0, N1')
    THE_MAP = {
        'N0': 'N0',
        'N1': 'N1',
        'N2': 'N1',
        'N3': 'N1',
    }
    # map N2/N3 to N1
    df['NSTAGE_STD'] = df['NSTAGE_STD'].map(THE_MAP)
    return df 

def normalize_field_pergroup_old(
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

def _normalize_field_pergroup(
    target_field: str, 
    norm_field: str,
    norm_meth: str,
    df: pd.DataFrame
    ) -> pd.DataFrame:
    df[norm_field] = 0

    # method 1: normalise values to range 0-1
    if norm_meth == 'range':
        df[norm_field] = (df[target_field] - df[target_field].min()) / (df[target_field].max() - df[target_field].min()) 

    # method2: normalise values as percentage of max 
    elif norm_meth == 'max':
        df[norm_field] = df[target_field] / df[target_field].max() 
    
    # method3: normalise values as proportion of total
    elif norm_meth == 'sum':
        df[norm_field] = df[target_field] / df[target_field].sum() 
    
    else:
        raise ValueError

    df[norm_field] = df[norm_field].fillna(value=0)
    return df

def _gen_counts_table(feature: str, valid: set[str], response: str, table: pd.DataFrame) -> pd.DataFrame:
    dfslice = table[table[feature].isin(valid)].copy()
    df = dfslice.groupby(feature)[response].value_counts().unstack().fillna(0).astype(int).reset_index().copy()
    df.columns = [feature, 'NO', 'YES']
    df['records'] = df['YES'] + df['NO']
    return df

##################
### STATISTICS ###
##################

def calculate_prevalence(
    feature: str, 
    valid: set[str], 
    response: str, 
    table: pd.DataFrame,
    ) -> pd.DataFrame: 
    df = _gen_counts_table(feature, valid, response, table)
    df = df.set_index(feature)
    df[s.PREVALENCE_FIELD] = (df['YES'] / (df['YES'] + df['NO'])) * 100
    return df

def calculate_ci(
    feature: str, 
    response: str, 
    df: pd.DataFrame,
    verbose: bool=False
    ) -> pd.DataFrame: 
    BUDGET = 1000
    all_features = sorted(list(df[feature].unique()))
    bframe = pd.DataFrame(columns=all_features)
    if verbose:
        print(f"\nRunning 95% ci estimation using {BUDGET} bootstrap samples.")
        print(f"- {df.shape[0]} records")
        print(f"- {len(all_features)} features")
    for i, feat in enumerate(all_features):
        if verbose:
            print(f"processed {i+1} features...", end='\r')
        fframe = df[df[feature]==feat][[response]].copy()
        fframe.columns = ['observed']
        fframe['observed'] = fframe['observed'].map({'YES': True, 'NO': False})
        fframe = fframe.astype(bool)
        obsvec = fframe['observed'].to_list()
        
        for i in range(BUDGET):
            fframe[f"bootstrap {i}"] = np.random.choice(obsvec, size=len(obsvec), replace=True)
        bframe[feat] = fframe.sum()

    if verbose:
        print(f"processed {i+1} features... done.")
    # print(bframe.iloc[:10, :10])
    assert bframe.isna().sum(axis=0).sum() == 0
    assert bframe.isna().sum(axis=1).sum() == 0

    data = []
    for feat in all_features:
        vals = bframe[feat].sort_values().to_list()
        ci_low = vals[int(BUDGET*0.025)]
        ci_high = vals[int(BUDGET*0.975)]
        data.append((feat, ci_low, bframe.loc['observed', feat], ci_high))
    ciframe = pd.DataFrame.from_records(data=data, columns=[feature, 'ci_low', 'observed', 'ci_high'])
    ciframe = ciframe.set_index(feature)
    return ciframe

def calculate_relrisk(
    feature: str, 
    valid: set[str], 
    response: str, 
    table: pd.DataFrame,
    ) -> pd.DataFrame: 
    df = _gen_counts_table(feature, valid, response, table)
    df = df.set_index(feature)
    df['risk'] = df['YES'] / df['records']
    feat = df[df['risk']==df['risk'].min()].index.values[0]
    control_cases = int(df.loc[feat, 'YES'])
    control_total = int(df.loc[feat, 'records'])
    for feat, row in df.iterrows():
        rr, ci_low, ci_high = _relrisk(
            feat_cases=int(row['YES']),
            feat_total=int(row['records']),
            control_cases=control_cases,
            control_total=control_total,
        )
        df.loc[feat, 'relRisk'] = rr
        df.loc[feat, 'relRiskLow'] = ci_low
        df.loc[feat, 'relRiskHigh'] = ci_high
    return df

def _relrisk(feat_cases: int, feat_total: int, control_cases: int, control_total: int) -> Tuple[float, float, float]:
    """
    feature: cancer_group or hist_cateogry 
                    feature background
    metastasis YES |   a   |     b    |
               NO  |   c   |     d    |
    """
    res = relative_risk(feat_cases, feat_total, control_cases, control_total)
    ci = res.confidence_interval(confidence_level=0.95)
    return res.relative_risk, ci.low, ci.high

# def calculate_logodds(
#     feature: str, 
#     valid: set[str], 
#     response: str, 
#     table: pd.DataFrame,
#     ) -> pd.DataFrame: 
#     """
#     Response variable must only have NaN, 'NO', 'YES' as values. 
#     Natural logarithm used. 
#     """
#     df = _gen_counts_table(feature, valid, response, table)
#     cohort_yes = table[table[response]=='YES'].shape[0]
#     cohort_no = table[table[response]=='NO'].shape[0]

#     # logodds
#     for i, feat in enumerate(df.index):
#         print(f"processed {i+1}/{df.shape[0]} features... ", end='\r')
#         or_stat, ci_low, ci_high = _logodds(
#             a=int(df.loc[feat, 'YES']),
#             b=int(df.loc[feat, 'NO']),
#             c=cohort_yes,
#             d=cohort_no,
#         )
#         df.loc[feat, 'logOdds'] = or_stat
#         df.loc[feat, 'logOddsLow'] = ci_low
#         df.loc[feat, 'logOddsHigh'] = ci_high
#     print(f"processed {i+1} features... done")

#     # final formatting
#     mask = df[df['logOdds'].isna()].index.to_list()
#     df.loc[mask, 'logOdds'] = df['logOdds'].min()-0.001
#     df.loc[mask, 'logOddsLow'] = df['logOddsLow'].min()-0.001
#     df.loc[mask, 'logOddsHigh'] = df['logOddsHigh'].min()-0.001
#     df = df.set_index(feature)
#     return df

# def _logodds(a: int, b: int, c: int, d: int) -> Tuple[float, float, float]:
#     """
#     feature: cancer_group or hist_cateogry 
#                     feature background
#     metastasis YES |   a   |     b    |
#                NO  |   c   |     d    |
#     """
#     res = odds_ratio([[a, b], [c, d]], kind='sample')
#     ci = res.confidence_interval(confidence_level=0.95)
#     # or_stat = np.nan if res.statistic == 0 or res.statistic == np.nan else math.log(res.statistic)
#     # ci_low = np.nan if ci.low == 0 or ci.low == np.nan else math.log(ci.low)
#     # ci_high = np.nan if ci.high == 0 or ci.high == np.nan else math.log(ci.high)
#     return res.statistic, ci.low, ci.high


def remove_exclusive_groups(tables: list[pd.DataFrame]) -> list[pd.DataFrame]:
    valid_groups = set(tables[0]['derived_group'].unique())
    for table in tables[1:]:
        valid_groups = valid_groups & set(table['derived_group'].unique())
    filt_tables = []
    for table in tables:
        filt = table[table['derived_group'].isin(valid_groups)]
        filt_tables.append(filt)
    return filt_tables


# def calculate_feature_relrisk(
#     feature: str, 
#     response: str, 
#     df: pd.DataFrame,
#     s: Settings
#     ) -> pd.DataFrame:

#     yn_df = df.groupby(by=[feature, response]).size().unstack(fill_value=0)
#     table = yn_df.reset_index()
#     if 'YES' not in table.columns:
#         table['YES'] = 0
#     if 'NO' not in table.columns:
#         table['NO'] = 0
#     table['records'] = table['YES'] + table['NO']
#     table['prevalence (%)'] = (table['YES'] / (table['YES'] + table['NO'])) * 100
#     table = table.set_index(feature, drop=True)

#     table = normalize_field_pergroup(
#         groups=s.COMPOUND_GROUP,
#         target_field=s.PREVALENCE_FIELD, 
#         norm_field=s.RELRISK_FIELD,
#         norm_meth=s.NORM_METH,
#         df=table,
#     )

#     return table

# def calculate_met_stats(
#     feature: str, 
#     response: str, 
#     df: pd.DataFrame,
#     cohort_yes: Optional[float]=None,
#     cohort_no: Optional[float]=None,
#     baseline_fval: Optional[str]=None
#     ) -> pd.DataFrame: 
#     yn_df = df.groupby(by=[feature, response]).size().unstack(fill_value=0)
#     prevs = yn_df.reset_index()
#     if 'YES' not in prevs.columns:
#         prevs['YES'] = 0
#     if 'NO' not in prevs.columns:
#         prevs['NO'] = 0
#     prevs['records'] = prevs['YES'] + prevs['NO']
#     prevs['prevalence (%)'] = (prevs['YES'] / (prevs['YES'] + prevs['NO'])) * 100
#     prevs = prevs.set_index(feature, drop=True)

#     if cohort_yes is not None and cohort_no is not None:
#         odds_stats = pd.DataFrame(index=prevs.index, columns=['OR_STAT', 'OR_CI_LOW', 'OR_CI_HIGH'])

#         for i, fval in enumerate(df[feature].unique()):
#             cont = pd.DataFrame(columns=['subset', 'reference'], index=['YES', 'NO'], data=[[0, 0],[0, 0]])
#             cont.loc['YES', 'reference'] = cohort_yes
#             cont.loc['YES', 'subset'] = prevs.loc[fval, 'YES']
#             cont.loc['NO', 'reference'] = cohort_no
#             cont.loc['NO', 'subset'] = prevs.loc[fval, 'NO']
#             res = odds_ratio(cont, kind='sample')
#             ci = res.confidence_interval(confidence_level=0.95)
#             odds_stats.loc[fval] = pd.Series({'OR_STAT': res.statistic, 'OR_CI_LOW': ci.low, 'OR_CI_HIGH': ci.high})
        
#         prevs = prevs.join(odds_stats)

#     elif baseline_fval is not None:
#         odds_stats = pd.DataFrame(index=prevs.index, columns=['OR_STAT', 'OR_CI_LOW', 'OR_CI_HIGH'])
#         baseline_yes = prevs.loc[baseline_fval, 'YES']
#         baseline_no = prevs.loc[baseline_fval, 'NO']
#         for i, fval in enumerate(df[feature].unique()):
#             if fval == baseline_fval:
#                 odds_stats.loc[fval] = pd.Series({'OR_STAT': 1, 'OR_CI_LOW': 1, 'OR_CI_HIGH': 1})
#                 continue 

#             cont = pd.DataFrame(columns=['subset', 'reference'], index=['YES', 'NO'], data=[[0, 0],[0, 0]])
#             cont.loc['YES', 'reference'] = baseline_yes
#             cont.loc['YES', 'subset'] = prevs.loc[fval, 'YES']
#             cont.loc['NO', 'reference'] = baseline_no
#             cont.loc['NO', 'subset'] = prevs.loc[fval, 'NO']
#             res = odds_ratio(cont, kind='sample')
#             ci = res.confidence_interval(confidence_level=0.95)
#             odds_stats.loc[fval] = pd.Series({'OR_STAT': res.statistic, 'OR_CI_LOW': ci.low, 'OR_CI_HIGH': ci.high})
        
#         prevs = prevs.join(odds_stats)

#     return prevs

def generate_ordered_pivot_tables(tables: list[pd.DataFrame], valuefield: str) -> list[pd.DataFrame]:
        
    CLUSTER_GROUPS   = True
    CLUSTER_FEATURES = False
    
    # normalise prevalence & pivot for each table
    pivot_tables = []
    for table in tables:
        pivottable = table.pivot(index=s.COMPOUND_GROUP, columns=s.COMPOUND_FEATURE, values=valuefield)
        pivottable = pivottable.fillna(0)
        pivottable = pivottable.reindex(sorted(pivottable.columns), axis=1)
        Y = pivottable.to_numpy()
        tablemax = np.where(np.isinf(Y), -np.Inf, Y).max()
        X = np.where(np.isinf(Y), tablemax, Y)
        ptable = pd.DataFrame(data=X, index=pivottable.index, columns=pivottable.columns)
        pivot_tables.append(ptable)
    
    # plot clustermap for first table to allow clustering
    table1 = pivot_tables[0]
    cm = sns.clustermap(
        table1, 
        col_cluster=CLUSTER_FEATURES, 
        row_cluster=CLUSTER_GROUPS, 
        metric="correlation",
        square=True,
    )
    plt.plot()
    plt.close()

    # get row/col order from clustermap
    rowinds = cm.dendrogram_row.reordered_ind if CLUSTER_GROUPS else list(range(table1.shape[0]))
    colinds = cm.dendrogram_col.reordered_ind if CLUSTER_FEATURES else list(range(table1.shape[1]))
    rowlabels = [table1.index[idx] for idx in rowinds]
    collables = [table1.columns[idx] for idx in colinds]
    
    # reorder pivot table rows/cols using new ordering
    pivot_tables = [t[collables] for t in pivot_tables]
    pivot_tables = [t.loc[rowlabels] for t in pivot_tables]
    return pivot_tables


def calculate_stats_grouped(
    groups: list[str],
    features: list[str], 
    response_field: str,
    df: pd.DataFrame, 
    groups_subset: Optional[dict]=None, 
    features_subset: Optional[dict]=None
    ) -> pd.DataFrame:
    
    # remove records where there is no value for any of the features.
    temp = df.dropna(subset=features)  
    temp = temp.dropna(subset=groups)  

    # filter groups to subset if required
    if groups_subset is not None:
        for gname, gvals in groups_subset.items():
            temp = temp[temp[gname].isin(gvals)]
    
    # filter features to subset if required
    if features_subset is not None:
        for fname, fvals in features_subset.items():
            if fname in features:
                temp = temp[temp[fname].isin(fvals)]

    # categorial variables only
    for feat in features:
        if str(temp.dtypes[feat]) != 'object':
            temp[feat] = temp[feat].apply(str)

    # create compound group if more than 1 'group'
    if len(groups) == 1:
        temp[s.COMPOUND_GROUP] = temp[groups[0]]
    else:
        temp[s.COMPOUND_GROUP] = temp[groups].agg(':'.join, axis=1)
    
    # create compound feature if more than 1 'feature'
    if len(features) == 1:
        temp[s.COMPOUND_FEATURE] = temp[features[0]]
    else:
        temp[s.COMPOUND_FEATURE] = temp[features].agg(':'.join, axis=1)

    # filter groups with too few records. 
    temp = temp.groupby(s.COMPOUND_GROUP).filter(lambda x: len(x) > s.THRESH_RECORDS)
    
    # calculate stats per group
    i = 0
    maintable = pd.DataFrame()
    groupvals = temp[s.COMPOUND_GROUP].unique()
    
    filtered = []
    # iter through each group class
    for gval in groupvals:
        i += 1
        temp_group = temp[temp[s.COMPOUND_GROUP]==gval][[s.COMPOUND_FEATURE, response_field]]
        stats = calculate_feature_stats(
            feature=s.COMPOUND_FEATURE, 
            response=response_field, 
            df=temp_group,
            s=s
        )
        num_failing_rec_thresh = sum(stats['records'] < s.THRESH_RECORDS)
        num_failing_yes_thresh = sum(stats['YES'] < s.THRESH_POSITIVE)
        nfeatures = stats.shape[0]
        
        # filter condition 1: 50% or greater features must have >thresh records. 
        if num_failing_rec_thresh / nfeatures > 0.5:
            filtered.append(gval)
            continue 
        # filter condition 2: 50% or greater features must have >thresh bm cases. 
        if num_failing_yes_thresh / nfeatures > 0.5:
            filtered.append(gval)
            continue 
        
        stats = stats.reset_index()
        stats[s.COMPOUND_GROUP] = gval
        maintable = pd.concat([maintable, stats], ignore_index=True)
        print(f'{i}/{len(groupvals)} subsets calculated', end='\r')

    print(f'\nRemoved {len(filtered)}/{len(groupvals)} groups')
    # for gval in filtered:
    #     print(f'-{gval}')

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

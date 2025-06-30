
import numpy as np
import pandas as pd
from typing import Tuple, Any




#############
### STATS ###
#############

# def tendency(df: pd.DataFrame, )

def relrisk(df: pd.DataFrame, grouping: str|None, predictor: str, response: str, baseval: str, banned: list[str]|None=None) -> pd.DataFrame:
    counts = df.groupby([grouping, predictor])[response].value_counts().unstack().fillna(0).astype(int).reset_index()
    counts.columns = [str(x) for x in counts.columns]
    if banned is not None:
        counts = counts[~counts[predictor].isin(banned)]
    counts['prop'] = counts['True'] / (counts['True']+counts['False']) * 100
    baseline_cases = counts[counts[predictor]==baseval].set_index(grouping)['True'].to_dict()
    baseline_props = counts[counts[predictor]==baseval].set_index(grouping)['prop'].to_dict()
    counts['norm'] = counts['prop'] / counts[grouping].map(baseline_props)
    valid = set([k for k, v in baseline_cases.items() if v>=5])
    counts = counts[counts[grouping].isin(valid)]
    return counts 

def prevalence(df: pd.DataFrame, predictor: str, response: str) -> pd.DataFrame: 
    counts = df.sort_values(response).groupby(predictor)[response].value_counts().unstack().fillna(0).astype(int).copy()
    counts.columns = [str(x) for x in counts.columns]
    counts['records'] = counts['True'] + counts['False']
    counts['stat'] = (counts['True'] / counts['records']) * 100
    return counts


#################################
### DATA LOAD & PREPROCESSING ###
#################################

NAMELUT = {

    # pure categorical
    'cancer_group': 'cancer_group_CAT',
    'hist_group': 'hist_group_CAT',
    'HER2_type': 'HER2_type_CAT',
    'sex': 'sex_CAT',

    # pure bool
    'local_ln_met': 'local_ln_met_BOOL',
    'distant_ln_met': 'distant_ln_met_BOOL',
    'brain_met': 'brain_met_BOOL',
    'bone_met': 'bone_met_BOOL',
    'liver_met': 'liver_met_BOOL',
    'lung_met': 'lung_met_BOOL',
    'other_met': 'other_met_BOOL',
    'any_met': 'any_met_BOOL',
    'ulceration': 'ulceration_BOOL',
    'perineural_invasion': 'perineural_invasion_BOOL',
    'adrenal_involvement': 'adrenal_involvement_BOOL',
    'major_vein_involvement': 'major_vein_involvement_BOOL',
    'capsule_invasion': 'capsule_invasion_BOOL',
    'chr19q_loh': 'chr19q_loh_BOOL',
    'chr1p_loh': 'chr1p_loh_BOOL',
    'pleural_effusion': 'pleural_effusion_BOOL',
    'B_symptoms': 'B_symptoms_BOOL',

    # categorical (mappable to NUM)
    'TSTAGE_STD': 'TSTAGE_CAT',
    'NSTAGE_STD': 'NSTAGE_CAT',
    'GSTAGE_STD': 'GSTAGE_CAT',
    'GRADE_STD': 'GRADE_CAT',
    'hGC_post_orchiectomy_elevation': 'hGC_elevation_post_orchiectomy_CAT',
    'LDH_post_orchiectomy_elevation': 'LDH_elevation_post_orchiectomy_CAT',
    'HER2_status': 'HER2_status_CAT',
    'peripheral_blood_involvement': 'peripheral_blood_involvement_CAT',
    'peritoneal_cytology': 'peritoneal_cytology_CAT',
    'pleural_invasion': 'pleural_invasion_CAT',
    
    # categorical (mappable to BOOL)
    'LDH_pretreatment': 'LDH_elevated_pretreat_CAT',
    'CEA_pretreat': 'CEA_elevated_pretreat_CAT',
    'ovarian_CA125': 'CA125_elevated_CAT',
    'AFP_pretreat_category': 'AFP_elevated_pretreat_CAT',
    'fibrosis_score': 'fibrosis_score_CAT',
    
    # continuous (always mappable to CAT and BOOL)
    'breslow_thick': 'breslow_thick_NUM',
    'mitotic_rate_melanoma': 'mitotic_rate_NUM',
    'PSA': 'PSA_NUM',
    'gleason': 'gleason_NUM',
    'tumor_deposits': 'tumor_deposits_NUM',
    'AFP_post_orchiectomy': 'AFP_post_orchiectomy_NUM',
    
}

def load_seer_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, sep='\t', header=0)
    df = _load_seer_data_filtering(df)
    df = _load_seer_data_redefine_fields(df)
    return df 

def _load_seer_data_filtering(df: pd.DataFrame) -> pd.DataFrame:
    cgroup_blacklist = ['Brain', 'Miscellaneous']
    hgroup_blacklist = ['unspecified neoplasms']
    
    print(f"Basic filtering")
    fpats, frecs = df['patient_id'].nunique(), df.shape[0]
    print(f"- Beginning: {fpats} patients, {frecs} records.")
    
    # banned cancer groups
    ipats, irecs = fpats, frecs
    df = df[~df['cancer_group'].isin(cgroup_blacklist)]
    fpats, frecs = df['patient_id'].nunique(), df.shape[0]
    print(f"- Removed {ipats-fpats} patients, {irecs-frecs} records where 'cancer_group' in {cgroup_blacklist}.")

    # banned histological groups
    ipats, irecs = fpats, frecs
    df = df[~df['hist_group'].isin(hgroup_blacklist)]
    fpats, frecs = df['patient_id'].nunique(), df.shape[0]
    print(f"- Removed {ipats-fpats} patients, {irecs-frecs} records where 'hist_group' in {hgroup_blacklist}.")

    # record year range
    ipats, irecs = fpats, frecs
    df = df.loc[df['diagnosis_year'] >= 2010]
    df = df.loc[df['diagnosis_year'] <= 2020]
    fpats, frecs = df['patient_id'].nunique(), df.shape[0]
    print(f"- Removed {ipats-fpats} patients, {irecs-frecs} records where 'diagnosis_year' not in range [2010, 2020].")
 
    # duplicate patient records 
    ipats, irecs = fpats, frecs
    df = df[~df.duplicated('patient_id', keep=False)]
    fpats, frecs = df['patient_id'].nunique(), df.shape[0]
    print(f"- Removed {ipats-fpats} patients, {irecs-frecs} records with duplicated patient_id.")
    # ipats, irecs = fpats, frecs
    # df = df[~df.duplicated(subset=['patient_id', 'cancer_type'])]
    # fpats, frecs = df['patient_id'].nunique(), df.shape[0]
    # print(f"- Removed {ipats-fpats} patients, {irecs-frecs} records with duplicated patient_id & cancer_type.")

    # primary marked as metastasis
    ipats, irecs = fpats, frecs
    MET_MAP = {
        'brain_met': ['Brain'], 
        'bone_met': ['Bones and Joints'], 
        'lung_met': ['Lung and Bronchus'],
        'liver_met': ['Liver'], 
    }
    for met, tissues in MET_MAP.items():
        mask = (df[met]==True) & (df['cancer_type'].isin(tissues))
        df = df[~mask]
    fpats, frecs = df['patient_id'].nunique(), df.shape[0]
    print(f"- Removed {ipats-fpats} patients, {irecs-frecs} records where primary cancer is marked as metastasis")
    
    print(f"- Final: {fpats} patients, {frecs} records.")
    return df.copy()

def _load_seer_data_redefine_fields(df: pd.DataFrame) -> pd.DataFrame:
    # redefine any_met
    df['any_met'] = df[['brain_met', 'bone_met', 'lung_met', 'liver_met', 'other_met']].any(axis=1)
    
    # local ln status
    df = format_local_ln_met(df)

    # age categorical -> float
    mask = df['age'].notna()
    df.loc[mask, 'age_NUM'] = df.loc[mask, 'age'].apply(cast_str_to_float_age)

    # age float -> categorical (rebinning)
    df.loc[mask, 'age_CAT'] = df.loc[mask, 'age_NUM'].apply(cast_float_age_to_bins, binwidth=10)
    
    # rename columns 
    df = df.rename(columns=NAMELUT)

    return df.copy()

def remove_all_NA_fields(df: pd.DataFrame) -> pd.DataFrame:
    # remove fields with all NA values
    all_na_fields = []
    for field in df.columns:
        if df[field].notna().sum() == 0:
            print(f"- [FAIL] {field}")
            all_na_fields.append(field)
    df = df.drop(all_na_fields, axis=1)

    return df.copy()

def select_categorical_feature_values(
    df: pd.DataFrame, 
    predictor: str,
    response: str,
    min_cases_total: int|None=None,
    min_cases_response: int|None=None,
    top: int|None=None,
    ) -> list:
    c_counts = pd.DataFrame(index=df[predictor].unique())
    c_counts['total'] = df[predictor].value_counts()
    c_counts[response] = df[df[response]==True][predictor].value_counts()
    c_counts = c_counts.fillna(0).astype(int)
    c_counts = c_counts.sort_values(response, ascending=False)

    if min_cases_total and min_cases_response:
        c_counts['valid'] = (c_counts['total']>=min_cases_total) & (c_counts[response]>=min_cases_response)
    elif min_cases_total:
        c_counts['valid'] = c_counts['total']>=min_cases_total
    elif min_cases_response:
        c_counts['valid'] = c_counts[response]>=min_cases_response
    else:
        raise ValueError('either min_cases_total or min_cases_brainmet cannot be None. ')

    if top: 
        c_counts['valid'] = (c_counts['valid']) & (c_counts.index.isin(c_counts.head(top).index.to_list()))
    
    print()
    if c_counts.shape[0] < 30:
        print(c_counts.head())
    else:
        print(c_counts.head(20))
        print(c_counts.tail(10))
    
    return sorted(c_counts[c_counts['valid']==True].index.to_list())
    

def subset_histology_groups(df: pd.DataFrame, min_cases_total: int|None=None, min_cases_brainmet: int|None=None) -> pd.DataFrame:
    assert min_cases_total or min_cases_brainmet
    field = 'hist_group_CAT' if 'hist_group_CAT' in df.columns else 'hist_group'
    response = 'brain_met_BOOL' if 'brain_met_BOOL' in df.columns else 'brain_met'
    c_counts = pd.DataFrame(index=df[field].unique())
    c_counts['total'] = df[field].value_counts()
    c_counts[response] = df[df[response]==True][field].value_counts()
    c_counts['valid'] = (c_counts['total']>=min_cases_total) & (c_counts[response]>=min_cases_brainmet)
    c_counts = c_counts.sort_values(response, ascending=False)
    valid = sorted(c_counts[c_counts['valid']==True].index.to_list())
    table = df[df[field].isin(valid)].copy()
    print()
    print(c_counts)
    return table

def format_predictors(df: pd.DataFrame) -> pd.DataFrame:
    df = format_categorical_to_numeric(df)
    df = format_categorical_to_bool(df)
    df = format_continuous_to_numeric_bool(df)
    df = format_bool_to_numeric(df)
    formatting_report_fields(df)
    return df

def format_categorical_to_numeric(df: pd.DataFrame) -> pd.DataFrame:
    # functions
    funclut = {
        'TSTAGE_CAT': cast_tstage_to_float,
        'NSTAGE_CAT': cast_nstage_to_float,
        'GSTAGE_CAT': cast_gstage_to_float,
        'GRADE_CAT': cast_grade_to_float,
        'hGC_elevation_post_orchiectomy_CAT': cast_hGC_to_float,
        'LDH_elevation_post_orchiectomy_CAT': cast_LDH_to_float,
        'HER2_status_CAT': cast_HER2_to_float,
        'peripheral_blood_involvement_CAT': cast_peripheral_blood_to_float,
        'peritoneal_cytology_CAT': cast_peritoneal_cytology_to_float,
        'pleural_invasion_CAT': cast_pleural_invasion_to_float,
    }

    # apply
    for field, func in funclut.items():
        if field not in df.columns:
            continue 
        newfield = field.replace('_CAT', '_NUM')
        if field == 'GRADE_CAT':
            mask = df['GRADE_CAT'].isin(['G1', 'G2', 'G3', 'G4'])
        else:
            mask = df[field].notna()
        df.loc[mask, newfield] = df.loc[mask, field].apply(func)
    
    return df.copy()

def format_categorical_to_bool(df: pd.DataFrame) -> pd.DataFrame:
    # functions
    funclut = {
        'LDH_elevated_pretreat_CAT': cast_2level_elevation_to_bool,
        'CEA_elevated_pretreat_CAT': cast_2level_elevation_to_bool,
        'AFP_elevated_pretreat_CAT': cast_2level_elevation_to_bool,
        'CA125_elevated_CAT': cast_2level_elevation_to_bool,
        'fibrosis_score_CAT': cast_fibrosis_to_bool,
    }

    # apply
    for field, func in funclut.items():
        if field not in df.columns:
            continue 
        mask = df[field].notna()
        newfield = field.replace('_CAT', '_BOOL')
        df.loc[mask, newfield] = df.loc[mask, field].apply(func)
    
    return df.copy()

def format_continuous_to_numeric_bool(df: pd.DataFrame) -> pd.DataFrame:
    # continuous (always mappable to CAT and BOOL)
    fields = [
        'breslow_thick_NUM',
        'mitotic_rate_NUM',
        'PSA_NUM',
        'gleason_NUM',
        'tumor_deposits_NUM',
        'AFP_post_orchiectomy_NUM',
    ]

    # mapping to 3 levels (categorical)
    for field in fields:
        if field not in df.columns:
            continue 
        newfield = field.replace('_NUM', '_CAT')
        mask = df[field].notna()
        df.loc[mask, newfield] = categorise(df.loc[mask, field], preferred_q=3)
        # sns.histplot(df, x=newfield)
        # plt.show()

    # mapping to 2 levels (high bool)
    for field in fields:
        if field not in df.columns:
            continue 
        newfield = field.replace('_NUM', '_BOOL')
        mask = df[field].notna()
        df.loc[mask, f"{newfield}_tmp"] = categorise(df.loc[mask, field], preferred_q=2)
        df.loc[mask, newfield] = df.loc[mask, f"{newfield}_tmp"].apply(lambda x: False if 'low' in x else True)
        df = df.drop(f"{newfield}_tmp", axis=1)
    
    return df.copy()

def format_bool_to_numeric(df: pd.DataFrame) -> pd.DataFrame:
    # Casting uncasted BOOL to NUM
    boolfields = [col for col in df.columns if col.endswith('_BOOL')]
    numfields = [col for col in df.columns if col.endswith('_NUM')]
    for field in boolfields:
        if field.replace('_BOOL', '_NUM') in numfields:
            print(f"ignoring {field} conversion to numeric.")
            continue 
        newfield = field.replace('_BOOL', '_NUM')
        mask = df[field].notna()
        df.loc[mask, newfield] = df.loc[mask][field].map({True: 1.0, False: 0.0})
    return df.copy()

def formatting_report_fields(df: pd.DataFrame) -> None:
    basefields = sorted(list(set([col.replace('_CAT', '').replace('_BOOL', '').replace('_NUM', '') for col in df.columns])))

    dtable_s = pd.DataFrame(data=False, index=basefields, columns=['CAT', 'NUM', 'BOOL'])
    for field in basefields:
        if f"{field}_CAT" in df.columns:
            dtable_s.loc[field, 'CAT'] = True
        if f"{field}_NUM" in df.columns:
            dtable_s.loc[field, 'NUM'] = True
        if f"{field}_BOOL" in df.columns:
            dtable_s.loc[field, 'BOOL'] = True

    print()
    print(dtable_s)

def format_local_ln_met(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use pathological first (if available), then clinical. 
    """
    temp = df[['NSTAGE_STD', 'regional_nodes', 'distant_ln_met']].copy()
    field = 'local_ln_met'

    # local lymph node status: via pathology assessment
    temp.loc[temp['regional_nodes']=='NEG', field] = False
    temp.loc[temp['regional_nodes'].isin(['POS_NODES', 'POS_ASPIRATION']), field] = True

    # local lymph node status:
    temp.loc[(temp[field].isna()) & (temp['NSTAGE_STD']=='N0'), field] = False
    temp.loc[(temp[field].isna()) & (temp['NSTAGE_STD'].isin(['N1', 'N2', 'N3'])), field] = True

    df[field] = temp[field]
    return df    


##################
### MISC FUNCS ###
##################

def add_jitter(arr, amount: float):
    return arr + np.random.uniform(-amount, amount, len(arr))


#################################
### CATEGORICAL -> NUMERIC ###
#################################
# also redefining bins 

def cast_str_to_float_age(age: str) -> float:
    if not isinstance(age, str):
        return age
    elif age == '90+ years':
        return 92.0
    elif age == '00 years':
        return 0.0
    elif age == '01-04 years':
        return 2.0
    else:
        lower_bound = int(age.split(' ')[0].split('-')[0])
        return float(lower_bound + 2)

def cast_bool_to_int(x: bool) -> int:
    return 1 if x else 0


# TO FLOAT
def cast_tstage_to_float(stage: str) -> float:
    if stage == 'Tis':
        return 0.0
    return float(stage[-1])

def cast_nstage_to_float(stage: str) -> float:
    return float(stage[-1])

def cast_grade_to_float(grade: str) -> float:
    return float(grade[-1])

def cast_gstage_to_float(stage: str) -> float:
    match stage: 
        case '0':
            return 0.0
        case 'I':
            return 1.0
        case 'II':
            return 2.0
        case 'III':
            return 3.0
        case 'IV':
            return 4.0
        case _:
            raise ValueError

def cast_hGC_to_float(text: str) -> float:
    match text: 
        case 'normal':
            return 0.0
        case 'low':
            return 1.0
        case 'medium':
            return 2.0
        case 'high':
            return 3.0
        case _:
            raise ValueError

def cast_LDH_to_float(text: str) -> float:
    match text: 
        case 'normal':
            return 0.0
        case 'low':
            return 1.0
        case 'high':
            return 2.0
        case _:
            raise ValueError

def cast_HER2_to_float(text: str) -> float:
    match text: 
        case 'Negative':
            return 0.0
        case 'Borderline/Unknown':
            return 1.0
        case 'Positive':
            return 2.0
        case _:
            raise ValueError

def cast_peripheral_blood_to_float(text: str) -> float:
    match text: 
        case 'no':
            return 0.0
        case 'low':
            return 1.0
        case 'high':
            return 2.0
        case _:
            raise ValueError

def cast_peritoneal_cytology_to_float(text: str) -> float:
    match text: 
        case 'negative':
            return 0.0
        case 'suspicious':
            return 1.0
        case 'malignant':
            return 2.0
        case _:
            raise ValueError

def cast_pleural_invasion_to_float(text: str) -> float:
    match text: 
        case 'PL0':
            return 0.0
        case 'PL1/PL2':
            return 1.5
        case 'PL3':
            return 3.0
        case _:
            raise ValueError
    

# TO BOOL
def cast_2level_elevation_to_bool(text: str) -> bool:
    match text: 
        case 'normal':
            return False
        case 'elevated':
            return True
        case _:
            raise ValueError

def cast_fibrosis_to_bool(text: str) -> bool:
    match text: 
        case 'Ishak 0-4;':
            return False
        case 'Ishak 5-6':
            return True
        case _:
            raise ValueError






#################################
### NUMERIC -> CATEGORICAL ###
#################################


# def map_3cat_to_numeric(text: str) -> float:
#     if 'low' in text:
#         return 0.0
#     elif 'mid' in text:
#         return 1.0
#     elif 'high' in text:
#         return 2.0
#     raise ValueError

def cast_float_age_to_bins(age: float, binwidth: int=10) -> str:
    for i in range(0, 110, binwidth):
        lower = i 
        upper = i + binwidth
        if age >= lower and age < upper:
            return f"{lower}-{upper-1} years"
    print(age)
    raise RuntimeError

def categorise(rawvals: pd.Series, preferred_q: int) -> pd.Series:
    try: 
        return categorise_pandas(rawvals, preferred_q)
    except:
        print('FALLBACK TO GRACE METHOD')
        return categorise_grace(rawvals, preferred_q)

def categorise_pandas(rawvals: pd.Series, q: int) -> pd.Series:
    nlabels_lut = {
        3: ['low', 'mid', 'high'],
        2: ['low', 'high'],
    } 
    
    try: 
        labels = nlabels_lut[q]
        catvals = pd.qcut(x=rawvals, q=q, labels=labels)
    except Exception as e: 
        if q == 2:
            raise e
        q -= 1
        labels = nlabels_lut[q]
        catvals = pd.qcut(x=rawvals, q=q, labels=labels)
    
    df = pd.DataFrame()
    df['raw'] = rawvals
    df['cat'] = catvals
    labels_fmt_lut = {}
    for l in labels:
        minval = df[df['cat']==l]['raw'].min()
        maxval = df[df['cat']==l]['raw'].max()
        l_fmt = f"{l} ({minval}-{maxval})"
        labels_fmt_lut[l] = l_fmt
    df['cat_fmt'] = df['cat'].map(labels_fmt_lut)
    # print(df.drop_duplicates(subset=['cat']))
    return df['cat_fmt']

def categorise_grace(rawvals: pd.Series, q: int) -> pd.Series:

    def _bad_cat_proportions(series: pd.Series, catranges: list) -> bool:
        observed = set(series.unique())
        expected = set([label for label, _, _ in catranges])
        if len(expected - observed) != 0:
            return True 
        return False
    
    if q == 3:
        catranges = categorise3(rawvals)
        catvals = rawvals.apply(numeric2categorical, ranges=catranges)
        if _bad_cat_proportions(catvals, catranges):
            catranges = categorise2(rawvals)
            catvals = rawvals.apply(numeric2categorical, ranges=catranges)
    elif q == 2: 
        catranges = categorise2(rawvals)
        catvals = rawvals.apply(numeric2categorical, ranges=catranges)
    else: 
        raise ValueError

    return catvals 

def categorise2(fieldvals: pd.Series) -> list[Tuple]:
    values = sorted(fieldvals.to_list())
    mod = len(values) % 2
    if mod == 0:
        midptr = len(values) // 2 - 1
    elif mod == 1:
        midptr = len(values) // 2
    else:
        raise RuntimeError
    
    # low 
    low_lower = values[0]
    low_upper = values[midptr]
    
    # high
    ptr = midptr
    while values[ptr] == low_upper and ptr < len(values):
        ptr += 1
    high_lower = values[ptr]
    high_upper = values[-1]

    if str(fieldvals.dtype).lower().startswith('int'):
        low_label = f"low ({low_lower}-{low_upper})"
        high_label = f"high ({high_lower}-{high_upper})"
    elif str(fieldvals.dtype).lower().startswith('float'):
        low_label = f"low ({low_lower:.1f}-{low_upper:.1f})"
        high_label = f"high ({high_lower:.1f}-{high_upper:.1f})"
    else:
        raise NotImplementedError

    return [
        (low_label, low_lower, low_upper),
        (high_label, high_lower, high_upper),
    ]

def categorise3(fieldvals: pd.Series) -> list[Tuple]:
    values = sorted(fieldvals.to_list())
    intdiv = len(values) // 3
    remain = len(values) % 3
    if remain == 0:
        idx_l = [intdiv-1, intdiv*2]
    elif remain == 1:
        idx_l = [intdiv, intdiv*2]
    elif remain == 2:
        idx_l = [intdiv, intdiv*2+1]
    else:
        raise RuntimeError
    
    # low 
    low_lower = values[0]
    low_upper = values[idx_l[0]]
    
    # high
    high_lower = values[idx_l[1]]
    high_upper = values[-1]

    # mid 
    mid_lower = min([x for x in values if x > low_upper])
    mid_upper = max([x for x in values if x < high_lower])

    # labels
    if str(fieldvals.dtype).lower().startswith('int'):
        low_label = f"low ({low_lower}-{low_upper})"
        mid_label = f"mid ({mid_lower}-{mid_upper})"
        high_label = f"high ({high_lower}-{high_upper})"
    elif str(fieldvals.dtype).lower().startswith('float'):
        low_label = f"low ({low_lower:.1f}-{low_upper:.1f})"
        mid_label = f"mid ({mid_lower:.1f}-{mid_upper:.1f})"
        high_label = f"high ({high_lower:.1f}-{high_upper:.1f})"
    else:
        raise RuntimeError

    return [
        (low_label, low_lower, low_upper),
        (mid_label, mid_lower, mid_upper),
        (high_label, high_lower, high_upper),
    ]

def numeric2categorical(x: Any, ranges: list[Tuple]) -> Any:
    if pd.isna(x):
        return x
    for cat, lower_bound, upper_bound in ranges:
        if x >= lower_bound and x <= upper_bound:
            return cat 
    raise ValueError


##################
### SUBSETTING ###
##################

def equalise_proportions(df: pd.DataFrame, boolfield: str, maxrows: int|None=None) -> pd.DataFrame:
    if maxrows is not None:
        top = df[df[boolfield]==True].head(maxrows//2).copy()
    else:
        top = df[df[boolfield]==True].copy()
    
    available = df[df[boolfield]==False].index.to_list()
    nitems = top.shape[0]
    idx_l = np.random.choice(available, size=nitems, replace=False)
    # print(sorted(idx_l[:5]))
    bot = df.loc[idx_l].copy()
    return pd.concat([top, bot], ignore_index=False)

def subset_max_records_per_comparison(df: pd.DataFrame, max: int=5000, bool_predictor: str|None=None) -> pd.DataFrame:
    import itertools
    fields = df.columns.to_list() if bool_predictor is None else [x for x in df.columns if x not in bool_predictor]
    comparisons = itertools.combinations(fields, 2)
    merged = pd.DataFrame(columns=df.columns)
    for f1, f2 in comparisons:
        if bool_predictor is None:
            dfslice = df[[f1, f2]].dropna().head(max).copy()
            merged = pd.concat([merged, dfslice], ignore_index=True)
        else:
            dfslice1 = df[df[bool_predictor]==True].dropna(subset=[f1, f2])[[f1, f2, bool_predictor]].head(max).copy()
            dfslice2 = df[df[bool_predictor]==False].dropna(subset=[f1, f2])[[f1, f2, bool_predictor]].head(max).copy()
            merged = pd.concat([merged, dfslice1], ignore_index=True)
            merged = pd.concat([merged, dfslice2], ignore_index=True)
    return merged.copy()





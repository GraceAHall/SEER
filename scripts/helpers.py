
import numpy as np
import pandas as pd
from typing import Tuple, Any


##################
### FORMATTING ###
##################

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


#############
### STATS ###
#############

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



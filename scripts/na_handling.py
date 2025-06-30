
import numpy as np
import pandas as pd 

from sklearn.impute import KNNImputer


def handle_na(dtable: pd.DataFrame, response: str, n_missing: int=0, n_neighbors: int=1, verbose: bool=False) -> pd.DataFrame:
    if verbose:
        summarise_na(dtable, response)

    # subset records to those with at most `n_missing` na values. 
    df = subset_missing(dtable, n_missing=n_missing, exclude=[])

    # impute if specified
    if n_missing > 0:
        assert n_neighbors > 0
        df_i = impute_na(df, n_neighbors)
    else:
        df_i = df

    return df_i.copy()

def summarise_na(dtable: pd.DataFrame, response: str) -> None:
    n_pos = (dtable[response]==True).sum()
    n_neg = (dtable[response]==False).sum()
    print()
    print(f"n records positive class: {n_pos}")
    print(f"n records negative class: {n_neg}")
    data = []
    for field in dtable.columns:
        if field == response:
            continue 
        total = dtable[field].notna().sum()
        res_t = dtable[dtable[response]==True][field].notna().sum()
        res_f = dtable[dtable[response]==False][field].notna().sum()
        data.append((field, total, f"{(res_t/n_pos)*100:.2f}%", f"{(res_f/n_neg)*100:.2f}%", res_t))

    fframe = pd.DataFrame.from_records(data=data, columns=['predictor', 'total', 'brain met TRUE', 'brain met FALSE', 'has brain met'])
    print()
    print(fframe.set_index('predictor'))

def subset_missing(dtable: pd.DataFrame, n_missing: int, exclude: list[str]) -> pd.DataFrame:
    # filter records missing too many values
    predictors = [x for x in dtable.columns if x not in exclude]
    dtable['n_missing'] = dtable[predictors].isna().sum(axis=1)
    dtable = dtable[dtable['n_missing']<=n_missing].copy()
    dtable_s = dtable.drop(['n_missing'], axis=1)
    dtable_s = dtable_s.reset_index(drop=True)
    return dtable_s.copy()

def impute_na(dtable: pd.DataFrame, n_neighbors: int) -> pd.DataFrame:
    """
    performs KNN imputation
    """
    imputer = KNNImputer(n_neighbors=n_neighbors)
    dtable_i = pd.DataFrame(imputer.fit_transform(dtable), columns=dtable.columns)

    if n_neighbors > 1:
        # fix imputed values so they're mapped to the closest observed value. 
        for field in dtable_i:
            valid_vals = dtable[dtable[field].notna()][field].unique()
            imput_vals = dtable_i[field].unique()
            lut = {}
            for i_val in imput_vals:
                diffs = [(v_val, abs(v_val-i_val)) for v_val in valid_vals]
                diffs = sorted(diffs, key=lambda x: x[1])
                lut[i_val] = diffs[0][0]
            dtable_i[field] = dtable_i[field].map(lut)

    return dtable_i.copy()

def report_imputation(dtable_raw: pd.DataFrame, dtable_imp: pd.DataFrame) -> None:
    print('\nresponse=True ---')
    for field in dtable_raw.columns:
        print()
        df = pd.DataFrame()
        if dtable_s[field].nunique() > 10:
            print(field)
            df['raw'] = dtable_raw[field].describe()
            df['imp'] = dtable_imp[field].describe()
            df = df.fillna(0).T
        else:
            df['raw'] = dtable_raw[field].value_counts(dropna=False)
            df['imp'] = dtable_imp[field].value_counts(dropna=False)
            raw_notna = dtable_raw[field].notna().sum()
            imp_notna = dtable_imp[field].notna().sum()
            df = df.fillna(0).T
            df['total'] = df.sum(axis=1)
            df.loc['raw', 'notna'] = raw_notna
            df.loc['imp', 'notna'] = imp_notna
        print(df)

def remove_invariant_predictors(df: pd.DataFrame, verbose: bool=False) -> pd.DataFrame:
    to_remove = []
    for field in df.columns:
        if df[field].nunique() < 2:
            to_remove.append(field)
    if verbose and len(to_remove) > 0:
        print('\nRemoving the following invariable predictors (only single value):')
        for field in to_remove:
            print(field)
    df = df.drop(to_remove, axis=1)
    return df.copy()
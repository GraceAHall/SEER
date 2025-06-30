
import pandas as pd 
from typing import Tuple

from abc import ABC, abstractmethod


class DtableGenerator(ABC):
    CANCER_PLACEHOLDER = 'other primary'
    HISTOLOGY_PLACEHOLDER = 'other histology'

    def __init__(self, df: pd.DataFrame, predictors: list[str], response: str) -> None:
        self.df = df
        self.predictors = predictors
        self.response = response


    @abstractmethod
    def generate(self) -> pd.DataFrame:
        ...
    
    @abstractmethod
    def _gather_predictors(self, dfslice: pd.DataFrame) -> Tuple[list[str], list[str]]:
        ...
    
    def _rename_predictors(self, dtable: pd.DataFrame) -> pd.DataFrame:
        remapper = {}
        for col in dtable.columns:
            if '_NUM' in col:
                remapper[col] = col.replace('_NUM', '')
        dtable = dtable.rename(columns=remapper)
        return dtable
        
    def _populate_dtable(self, dfslice: pd.DataFrame, catpreds: list[str], numpreds: list[str]) -> pd.DataFrame:
        # dtable
        dtable = pd.DataFrame(index=dfslice.index)
        
        # lift numeric
        for pred in numpreds:
            dtable[pred] = dfslice[pred]
        
        # one-hot encode categorical
        for field in catpreds:
            fvals = sorted(list(dfslice[field].dropna().unique()))
            for val in fvals:
                dtable[val] = 0
                mask = dfslice[field]==val
                dtable.loc[mask, val] = 1

        # add reponse variable
        dtable[self.response] = dfslice[self.response]
        return dtable


class AllGroupsDtableGenerator(DtableGenerator):

    def __init__(self, df: pd.DataFrame, valid_cgroups: list[str], valid_hgroups: list[str], predictors: list[str], response: str) -> None:
        super().__init__(df, predictors, response)
        self.valid_cgroups = valid_cgroups
        self.valid_hgroups = valid_hgroups
    
    def generate(self) -> pd.DataFrame:
        dfslice = self.df.copy()
        dfslice = dfslice[dfslice[self.response].notna()]
        dfslice = dfslice[dfslice['cancer_group_CAT'].notna()]
        dfslice = dfslice[dfslice['hist_group_CAT'].notna()]
        dfslice = dfslice.reset_index(drop=True).copy()

        # reassign cancer and histology memberships for low-prevalence groups
        dfslice = self._reassign_cancer_groups(dfslice)
        dfslice = self._reassign_hist_groups(dfslice)
        print()
        print(dfslice['cancer_group_CAT'].value_counts(dropna=False))
        print()
        print(dfslice['hist_group_CAT'].value_counts(dropna=False))

        # predictors
        catpreds, numpreds = self._gather_predictors(dfslice)
        print(catpreds)
        print(numpreds)

        dtable = self._populate_dtable(dfslice, catpreds, numpreds)
        dtable = self._rename_predictors(dtable)
        return dtable.copy()
    
    def _reassign_cancer_groups(self, dfslice: pd.DataFrame) -> pd.DataFrame:
        mask = ~dfslice['cancer_group_CAT'].isin(self.valid_cgroups)
        dfslice.loc[mask, 'cancer_group_CAT'] = self.CANCER_PLACEHOLDER
        return dfslice
    
    def _reassign_hist_groups(self, dfslice: pd.DataFrame) -> pd.DataFrame:
        mask = ~dfslice['hist_group_CAT'].isin(self.valid_hgroups)
        dfslice.loc[mask, 'hist_group_CAT'] = self.HISTOLOGY_PLACEHOLDER
        return dfslice

    def _gather_predictors(self, dfslice: pd.DataFrame) -> Tuple[list[str], list[str]]:
        basefields = [col.replace('_CAT', '').replace('_BOOL', '').replace('_NUM', '') for col in dfslice.columns]
        basefields = sorted(list(set(basefields)))
        catpreds = []
        numpreds = []
        for field in basefields:
            if field not in self.predictors:
                continue
            catfield = f"{field}_CAT"
            numfield = f"{field}_NUM"
            if numfield in dfslice.columns:
                nvals = dfslice[dfslice[numfield].notna()][numfield].nunique()
                if nvals >= 2:
                    numpreds.append(numfield)
            else:
                nvals = dfslice[dfslice[catfield].notna()][catfield].nunique()
                if nvals >= 2:
                    catpreds.append(catfield)
        return catpreds, numpreds


class SingleGroupDtableGenerator(DtableGenerator):
    HISTOLOGY_MIN_BRAINMET_OBS = 20
    HISTOLOGY_MAX_GROUPS = 3
    
    def __init__(self, df: pd.DataFrame, predictors: list[str], response: str) -> None:
        super().__init__(df, predictors, response)
    
    def generate(self) -> pd.DataFrame:
        """
        creating DTable for logistic regression / decision tree:
        if only CAT field (no NUM/BOOL), one-hot encode.
        else, assert NUM field and use this. 
        """
        dfslice = self.df.copy()
        dfslice = dfslice[dfslice[self.response].notna()]
        dfslice = dfslice.reset_index(drop=True).copy()
        catpreds, numpreds = self._gather_predictors(dfslice)
        if 'hist_group_CAT' in catpreds:
            dfslice = self._reassign_hist_groups(dfslice)
        dtable = self._populate_dtable(dfslice, catpreds, numpreds)
        dtable = self._rename_predictors(dtable)
        return dtable.copy()

    def _gather_predictors(self, dfslice: pd.DataFrame) -> Tuple[list[str], list[str]]:
        basefields = [col.replace('_CAT', '').replace('_BOOL', '').replace('_NUM', '') for col in dfslice.columns]
        basefields = sorted(list(set(basefields)))
        catpreds = []
        numpreds = []
        for field in basefields:
            if field not in self.predictors:
                continue 
            catfield = f"{field}_CAT"
            numfield = f"{field}_NUM"
            if numfield in dfslice.columns:
                nvals = dfslice[dfslice[numfield].notna()][numfield].nunique()
                if nvals >= 2:
                    numpreds.append(numfield)
            else:
                nvals = dfslice[dfslice[catfield].notna()][catfield].nunique()
                if nvals >= 2:
                    catpreds.append(catfield)
        return catpreds, numpreds
    
    def _reassign_hist_groups(self, dfslice: pd.DataFrame) -> pd.DataFrame:
        # remove low freq hist groups    
        hcounts = dfslice[dfslice[self.response]==True]['hist_group_CAT'].value_counts().sort_values(ascending=False)
        retain = hcounts[hcounts>=self.HISTOLOGY_MIN_BRAINMET_OBS].index.to_list()
        retain = retain[:self.HISTOLOGY_MAX_GROUPS]
        
        mask = dfslice['hist_group_CAT'].notna()
        if len(retain) == 0:
            print(f"\nNot retaining hist_group_CAT")
            dfslice.loc[mask, 'hist_group_CAT'] = self.HISTOLOGY_PLACEHOLDER
        else:
            print(f"\nRetaining the following hist_group_CAT values")
            for hgroup in retain:
                print(f"- {hgroup} ({hcounts[hgroup]} records)")
            dfslice.loc[mask, 'hist_group_CAT'] = dfslice.loc[mask, 'hist_group_CAT'].apply(lambda x: x if x in retain else self.HISTOLOGY_PLACEHOLDER)
        return dfslice.copy()



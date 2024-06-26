
from __future__ import annotations
from typing import Optional, Any
from dataclasses import dataclass, fields
from functools import cached_property
from util_enums import Grade, RegionalNodes, Behavior, Source
from util_consts import SEP_CHAR, ISEP_CHAR, NA_CHAR

### SETTINGS FOR NOTEBOOKS ###
@dataclass 
class Settings:
    RATE_FIELD = 'prevalence (%)'
    NORM_FIELD = 'norm'
    NORM_METH = 'sum'
    COMPOUND_FEATURE = 'derived_feature'
    COMPOUND_GROUP = 'derived_group'
    THRESH_RECORDS = 1000
    THRESH_POSITIVE = 3


### RECORD LEVEL ###

@dataclass
class SeerRecord:
    patient_id: int 
    patient_death_year: Optional[int]
    diagnosis_year: int 
    followup_year: int 
    diagnosis_agebin: str 
    cancer_type: str
    cancer_group: str
    primary_type: str
    primary_group: str
    t_stage_ajcc: Optional[str]
    n_stage_ajcc: Optional[str]
    g_stage_ajcc: Optional[str]
    t_stage_src: Source
    n_stage_src: Source
    g_stage_src: Source
    grade: Grade
    grade_src: Source
    regional_nodes: RegionalNodes
    regional_nodes_examined: Optional[int]
    regional_nodes_positive: Optional[int]
    behavior: Behavior
    num_malignant_tumors: int
    num_benign_tumors: int
    psa: Optional[float]
    breast_subtype: Optional[str]
    hist_type: int 
    hist_cateogry: str
    brain_met: Optional[bool]
    bone_met: Optional[bool]
    lung_met: Optional[bool]
    liver_met: Optional[bool]
    distant_ln: Optional[bool]

    def tostr(self) -> str:
        flist = [getattr(self, f.name) for f in fields(SeerRecord)]
        for idx, val in enumerate(flist):
            if isinstance(val, Source):
                flist[idx] = val.value
            elif isinstance(val, Behavior):
                flist[idx] = val.name
            elif isinstance(val, Grade | RegionalNodes):
                flist[idx] = None if val in [Grade.NA, RegionalNodes.NA] else val.name 
        flist = [str(x) if x is not None else NA_CHAR for x in flist]
        return SEP_CHAR.join(flist)
    
    @classmethod
    def fromstr(cls, line: str) -> SeerRecord:

        # INT_FIELDS = [
        #     'patient_id', 'patient_death_year', 'diagnosis_year', 'num_malignant_tumors', 
        #     'num_benign_tumors', 'hist_type', 'primary_site'
        # ]
        # FLOAT_FIELDS = ['psa']
        # BOOL_FIELDS = ['brain_met', 'bone_met', 'lung_met', 'liver_met', 'distant_ln']

        lsplit = line.strip().split(SEP_CHAR)
        flist = [(f.name, f.type) for f in fields(SeerRecord)]
        typecorrect_values = []
        for (fname, ftype), val in zip(flist, lsplit):
            # str -> int
            print()
        return SeerRecord(*typecorrect_values)




### PATIENT LEVEL ####



BAD_SITES = ['Miscellaneous']

"""
pid     death   year    T       N       G       Grade   Label       BrainMet

124     2011    2003    .       .       .       NA      Non-Hodgkin Lymphoma    False
124     2011    2007    Tis     N0      0       NA      Breast  False
124     2011    2010    T3      N0      IIB     NA      Breast  False

311     2015    2004    T3      N0(i+)  IIB     NA      Breast  False
311     2015    2013    TX      NX      .       NA      Breast  False

1030    .       2015    T1a     N0      IA      NA      Skin    False
1030    .       2017    T1c     N0      IA      CLINICAL        Breast  False
1030    .       2017    T1a     N0      IA      CLINICAL        Skin    False
1030    .       2019    T1a     N0      IA      NA      Skin    False
1030    .       2020    Tis     N0      0       NA      Skin    False
1030    .       2021    T3      N0      IA      NA      Breast  False

1009    2021    2013    T1c     N0      II      NA      Prostate        False
1009    2021    2019    T3      N2      IV      NA      Ureter  False

"""



# brainmet means the priamry
class Patient:

    def __init__(self, pid: int) -> None:
        self.patient_id = pid
        self.death_year: Optional[int] = None
        self.behavior: Behavior = Behavior.BENIGN
        self.num_malignant_tumors: int = 0
        self.num_benign_tumors: int = 0
        self.records: list[SeerRecord] = []

    def update(self, record: SeerRecord) -> None:
        # update attributes
        if self.death_year is None:
            self.death_year = record.patient_death_year
        if record.behavior.value > self.behavior.value:
            self.behavior = record.behavior
        self.num_malignant_tumors = max(self.num_malignant_tumors, record.num_malignant_tumors)
        self.num_benign_tumors = max(self.num_benign_tumors, record.num_benign_tumors)
        
        # update records
        self.records.append(record)
        self.records.sort(key=lambda x: x.diagnosis_year)

    def clean(self) -> None:
        cleaned_records = []
        for record in self.records:
            cleaned_records.append(record)
            if record.brain_met:
                break
        self.records = cleaned_records
    
    @cached_property
    def first_tumor(self) -> SeerRecord:
        return self.records[0]
    
    @cached_property
    def last_tumor(self) -> SeerRecord:
        return self.records[-1]
    
    @cached_property
    def first_tumor_site(self) -> str:
        site1 = self.records[0].cancer_type
        if len(self.records) == 1 or site1 not in BAD_SITES:
            return site1 
        
        for rec in self.records[1:]:
            if rec.cancer_type not in BAD_SITES:
                return rec.cancer_type
        return site1 
    
    def todict(self) -> dict[str, Any]:
        return {
            # patient level info
            'patient_id': self.patient_id,
            'death_year': self.death_year,
            'num_malignant_tumors': self.num_malignant_tumors,
            'num_benign_tumors': self.num_benign_tumors,
            'behavior': self.behavior.name,

            # brain met info
            'bm_status': 'YES' if self.records[-1].brain_met else 'NO',
            'bm_existing': 'YES' if self.records[0].brain_met else 'NO',
            'bm_developed': 'YES' if self.records[-1].brain_met and not self.records[0].brain_met else 'NO',
            
            # records
            'num_records': len(self.records),
            'timepoint_first': self.records[0].diagnosis_year,
            'timepoint_last': self.records[-1].diagnosis_year,
            'sites': ISEP_CHAR.join([r.cancer_type for r in self.records]),
            'diag_years': ISEP_CHAR.join([str(r.diagnosis_year) for r in self.records]),
            'diag_agebins': ISEP_CHAR.join([r.diagnosis_agebin.replace(' years', '') for r in self.records]),
            't_stages': ISEP_CHAR.join([r.t_stage_ajcc if r.t_stage_ajcc is not None else NA_CHAR for r in self.records]),
            'n_stages': ISEP_CHAR.join([r.n_stage_ajcc if r.n_stage_ajcc is not None else NA_CHAR for r in self.records]),
            'g_stages': ISEP_CHAR.join([r.g_stage_ajcc if r.g_stage_ajcc is not None else NA_CHAR for r in self.records]),
            'grades': ISEP_CHAR.join([r.grade.name if r.grade.name != Grade.NA else NA_CHAR for r in self.records]),
            'grades': ISEP_CHAR.join([r.grade.name if r.grade.name != Grade.NA else NA_CHAR for r in self.records]),
            'hist_types': ISEP_CHAR.join([str(r.hist_type) for r in self.records]),
            'regnodes': ISEP_CHAR.join([r.regional_nodes.name if r.regional_nodes.name != RegionalNodes.NA else NA_CHAR for r in self.records]),
        }



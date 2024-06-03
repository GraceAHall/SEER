
from __future__ import annotations
from typing import Optional, Any
from dataclasses import dataclass
from functools import cached_property
from util_enums import Grade, RegionalNodes, Behavior, Source
from util_consts import SEP_CHAR, ISEP_CHAR, NA_CHAR

@dataclass
class Record:
    patient_id: int 
    patient_death_year: Optional[int]
    diagnosis_year: int 
    diagnosis_agebin: str 
    site: str
    t_stage_ajcc: Optional[str]
    n_stage_ajcc: Optional[str]
    g_stage_ajcc: Optional[str]
    t_stage_src: Source
    n_stage_src: Source
    g_stage_src: Source
    hist_type: int 
    hist_cateogry: str
    grade: Grade
    grade_src: Source
    regional_nodes: RegionalNodes
    behavior: Behavior
    num_malignant_tumors: int
    num_benign_tumors: int
    site_category: str
    primary_site: int
    brain_met: bool

    def tostr(self) -> str:
        fields = [
            self.patient_id,
            self.patient_death_year,
            self.diagnosis_year,
            self.diagnosis_agebin,
            self.site,
            self.t_stage_ajcc,
            self.n_stage_ajcc,
            self.g_stage_ajcc,
            self.t_stage_src.value,
            self.n_stage_src.value,
            self.g_stage_src.value,
            self.hist_type,
            self.hist_cateogry,
            None if self.grade == Grade.NA else self.grade.name,
            self.grade_src.value,
            None if self.regional_nodes == RegionalNodes.NA else self.regional_nodes.name,
            self.behavior.name,
            self.num_malignant_tumors,
            self.num_benign_tumors,
            self.site_category,
            self.primary_site,
            self.brain_met
        ]
        items = [str(x) if x is not None else NA_CHAR for x in fields]
        return SEP_CHAR.join(items)
    
    @classmethod
    def fromstr(cls, line: str) -> Record:
        ln = line.strip().split(SEP_CHAR)
        return Record(
            patient_id=int(ln[0]),
            patient_death_year=int(ln[1]) if ln[1] != NA_CHAR else None,
            diagnosis_year=int(ln[2]),
            diagnosis_agebin=ln[3],
            site=ln[4],
            t_stage_ajcc=ln[5] if ln[5] != NA_CHAR else None,
            n_stage_ajcc=ln[6] if ln[6] != NA_CHAR else None,
            g_stage_ajcc=ln[7] if ln[7] != NA_CHAR else None,
            t_stage_src=Source.fromstr(ln[8]),
            n_stage_src=Source.fromstr(ln[9]),
            g_stage_src=Source.fromstr(ln[10]),
            hist_type=int(ln[11]),
            hist_cateogry=str(ln[12]),
            grade=Grade.fromstr(ln[13]),
            grade_src=Source.fromstr(ln[14]),
            regional_nodes=RegionalNodes.fromstr(ln[15]),
            behavior=Behavior.fromstr(ln[16]),
            num_malignant_tumors=int(ln[17]),
            num_benign_tumors=int(ln[18]),
            site_category=ln[19],
            primary_site=int(ln[20]),
            brain_met=eval(ln[21])
        )

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
        self.records: list[Record] = []

    def update(self, record: Record) -> None:
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
    def first_tumor(self) -> Record:
        return self.records[0]
    
    @cached_property
    def last_tumor(self) -> Record:
        return self.records[-1]
    
    @cached_property
    def first_tumor_site(self) -> str:
        site1 = self.records[0].site
        if len(self.records) == 1 or site1 not in BAD_SITES:
            return site1 
        
        for rec in self.records[1:]:
            if rec.site not in BAD_SITES:
                return rec.site
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
            'sites': ISEP_CHAR.join([r.site for r in self.records]),
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



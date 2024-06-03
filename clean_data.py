
from __future__ import annotations
from typing import Optional, Tuple
from dataclasses import fields
import re 

from util_classes import Record
from util_enums import Grade, Behavior, RegionalNodes, Source
from util_maps import (
    TSTAGE_AJCC,
    TSTAGE_AJCC7th_AJCC_MAP,
    TSTAGE_SEER_AJCC_MAP,
    TSTAGE_EOD_AJCC_MAP,
    NSTAGE_AJCC,
    NSTAGE_SEER_AJCC_MAP,
    NSTAGE_EOD_AJCC_MAP,
    GSTAGE_AJCC,
    GSTAGE_SEER_AJCC_MAP,
    GSTAGE_EOD_AJCC_MAP,
    GRADE_SEER_STD_MAP,
    GRADE_NAACCR_STD_MAP,
    SITE_CATEGORY_MAP
)

# INFILE = '/home/grace/work/brainmets/SEER/BrainMetsQueryFull.sample.txt'
# OUTFILE = '/home/grace/work/brainmets/SEER/BrainMetsQueryFull.sample.fmt.tsv'
import sys
INFILE = sys.argv[1]
OUTFILE = sys.argv[2]
 
############
### MAPS ###
############

############
### MAIN ###
############

def main() -> None:
    infp = open(INFILE, 'r')
    outfp = open(OUTFILE, 'w')
    i = 0
    outfp.write('\t'.join([f.name for f in fields(Record)]) + '\n')
    line = infp.readline()
    while line:
        if i % 100000 == 0:
            print(f'Processed {i} records', end='\r')
        record = gen_record(line)
        outfp.write(record.tostr() + '\n')
        line = infp.readline()
        i += 1
    infp.close()
    outfp.close()

###############
### PARSING ###
###############

"""
DATA_FIELDS:
[0]     pid             record_number   age                 diagnosis_year  death_year
[5]     site            Behavior        SEER_Mets_DXbrain   T_AJCC_6th      N_AJCC_6th      
[10]    T_AJCC_7th      N_AJCC_7th      T_SEER_Comb         N_SEER_Comb     T_EOD           
[15]    N_EOD           Stage_6th       Stage_7th           Stage_SEER1     Stage_SEER2
[20]    Total_Mal       Total_Ben       Hist_type           Reg_Nodes_Exam  Reg_Nodes_Pos
[25]    Grade_recode    Grade_Clin      Grade_Path       
"""

def gen_record(line: str) -> Record:
    lsplit = line.strip().split('\t')
    t_stage, t_src = get_stage_ajcc(lsplit[8], lsplit[10], lsplit[12], lsplit[14], 't')
    n_stage, n_src = get_stage_ajcc(lsplit[9], lsplit[11], lsplit[13], lsplit[15], 'n')
    g_stage, g_src = get_stage_ajcc(lsplit[16], lsplit[17], lsplit[18], lsplit[19], 'g')
    grade, grade_src = get_grade(lsplit)
    return Record(
        patient_id = int(lsplit[0]),
        diagnosis_agebin = get_age_bin(lsplit),
        diagnosis_year = get_diagnosis_year(lsplit),
        site = get_site(lsplit),
        site_category = get_site_category(lsplit),
        primary_site = get_primary_site(lsplit),
        t_stage_ajcc = t_stage,
        n_stage_ajcc = n_stage,
        g_stage_ajcc = g_stage,
        grade = grade,
        t_stage_src = t_src,
        n_stage_src = n_src,
        g_stage_src = g_src,
        grade_src = grade_src,
        hist_type = get_hist_type(lsplit),
        hist_cateogry = get_hist_category(lsplit),
        regional_nodes = get_regional_nodes(lsplit),
        behavior = get_behavior(lsplit),
        patient_death_year = get_death_year(lsplit),
        num_malignant_tumors = get_malignant_tumors_count(lsplit),
        num_benign_tumors = get_benign_tumors_count(lsplit),
        brain_met = get_brain_met(lsplit)
    )

def get_age_bin(lsplit: list[str]) -> str:
    return lsplit[2]

def get_death_year(lsplit: list[str]) -> Optional[int]:
    if lsplit[4].isdigit():
        return int(lsplit[4])
    return None

def get_diagnosis_year(lsplit: list[str]) -> int:
    return int(lsplit[3])

def get_site(lsplit: list[str]) -> str:
    return lsplit[5]

def get_site_category(lsplit: list[str]) -> str:
    return SITE_CATEGORY_MAP[lsplit[5]]

def get_primary_site(lsplit: list[str]) -> int:
    return int(lsplit[28])

def get_t_stage_raw(lsplit: list[str]) -> Tuple[str|None, str]:
    # ajcc (2004-2015)
    ajcc_6th, ajcc_7th = lsplit[8], lsplit[10]
    if ajcc_6th == 'Blank(s)' and ajcc_7th != 'Blank(s)':
        raise RuntimeError
    ajcc = None if ajcc_6th in ['NA', 'Blank(s)'] else ajcc_6th 
    if ajcc is not None:
        ajcc = 'Tis' if ajcc in ['Tispd', 'Tispu'] else ajcc
        return ajcc, 'ajcc'
    
    # seer (2016-2017)
    seer = None if lsplit[12] in ['Not applicable', 'Blank(s)'] else lsplit[12]
    if seer is not None:
        return seer, 'seer'
    
    # eod (2018+)
    eod = None if lsplit[14] in ['88', 'Blank(s)'] else lsplit[14]
    if eod is not None:
        return eod, 'eod'

    return None, 'neither'

BAD_STAGE_AJCC = ['T0', 'TX']
NA_STAGE_AJCC = ['Blank(s)', 'NA', 'UNK Stage']
NA_STAGE_SEER = ['Blank(s)', 'Not applicable', '99']
NA_STAGE_EOD = ['Blank(s)', '88', '99', 'DMS code 90 (invalid inputs)']

def _tstage_ajcc7th_to_ajcc6th(stage: str) -> str:
    if stage in TSTAGE_AJCC:
        return stage 
    return TSTAGE_AJCC7th_AJCC_MAP[stage]

def _tstage_seer_to_ajcc6th(stage: str) -> str:
    stage = re.sub(r'^(c|p)', '', stage)
    if stage == 'X':
        return 'TX'
    t_stage = 'T' + stage.lower()
    return t_stage if t_stage in TSTAGE_AJCC else TSTAGE_SEER_AJCC_MAP[stage] 

def _tstage_eod_to_ajcc6th(stage: str) -> str:
    return stage if stage in TSTAGE_AJCC else TSTAGE_EOD_AJCC_MAP[stage] 

def _nstage_seer_to_ajcc6th(stage: str) -> str:
    stage = re.sub(r'^(c|p)', '', stage)
    if stage == 'X':
        return 'NX'
    n_stage = 'N' + stage.lower()
    return n_stage if n_stage in NSTAGE_AJCC else NSTAGE_SEER_AJCC_MAP[stage] 

def _nstage_eod_to_ajcc6th(stage: str) -> str:
    return stage if stage in NSTAGE_AJCC else NSTAGE_EOD_AJCC_MAP[stage] 

def _gstage_seer_to_ajcc6th(stage: str) -> str:
    stage = re.sub(r'^1', 'I', stage)
    stage = re.sub(r'^2', 'II', stage)
    stage = re.sub(r'^3', 'III', stage)
    stage = re.sub(r'^4', 'IV', stage)
    return stage if stage in GSTAGE_AJCC else GSTAGE_SEER_AJCC_MAP[stage] 

def _gstage_eod_to_ajcc6th(stage: str) -> str:
    stage = re.sub(r'^1', 'I', stage)
    stage = re.sub(r'^2', 'II', stage)
    stage = re.sub(r'^3', 'III', stage)
    stage = re.sub(r'^4', 'IV', stage)
    return stage if stage in GSTAGE_AJCC else GSTAGE_EOD_AJCC_MAP[stage]

def get_stage_ajcc(ajcc_6th: str, ajcc_7th: str, seer: str, eod: str, category: str) -> Tuple[str|None, Source]:
    """returns t-stage as ajcc 6th edition (2004-2015)"""
    assert category in ['t', 'n', 'g']
    
    # ajcc
    ajcc_6th = None if ajcc_6th in NA_STAGE_AJCC else ajcc_6th     # type: ignore
    ajcc_7th = None if ajcc_7th in NA_STAGE_AJCC else ajcc_7th     # type: ignore
    
    if ajcc_6th and ajcc_7th:
        if ajcc_6th in BAD_STAGE_AJCC and ajcc_7th not in BAD_STAGE_AJCC:
            return _tstage_ajcc7th_to_ajcc6th(ajcc_7th), Source.NA
    if ajcc_6th:
        return ajcc_6th, Source.NA
    
    # seer
    seer = None if seer in NA_STAGE_SEER else seer                 # type: ignore
    if seer:
        if seer.startswith('c'):
            src = Source.CLINICAL
        elif seer.startswith('p'):
            src = Source.PATHOLOGICAL
        else:
            src = Source.NA
        
        if category == 't':
            return _tstage_seer_to_ajcc6th(seer), src
        elif category == 'n':
            return _nstage_seer_to_ajcc6th(seer), src
        else:
            return _gstage_seer_to_ajcc6th(seer), src
        
    # eod
    eod = None if eod in NA_STAGE_EOD else eod                     # type: ignore
    if eod:
        if category == 't':
            return _tstage_eod_to_ajcc6th(eod), Source.NA
        elif category == 'n':
            return _nstage_eod_to_ajcc6th(eod), Source.NA
        else:
            return _gstage_eod_to_ajcc6th(eod), Source.NA

    # No information
    return None, Source.NA
    
def get_hist_type(lsplit: list[str]) -> int:
    return int(lsplit[22])

def get_hist_category(lsplit: list[str]) -> str:
    return lsplit[29]

def get_grade(lsplit: list[str]) -> Tuple[Grade, Source]:
    """
    Grade is a measure of the aggressiveness of the tumor. 
    
    'Blank(s)'
    'Unknown'

    General Mapping ---
    NAACCR  SEER                                                                STD
    1,A     Well differentiated; Grade I                                        G1
    2,B     Moderately differentiated; Grade II                                 G2
    3,C     Poorly differentiated; Grade III                                    G3
    4,D     Undifferentiated; anaplastic; Grade IV                              G4
    9,9     Unknown                                                             None
    5       T-cell                                                              T_cell
    6       B-cell; pre-B; B-precursor                                          B_cell    
    7       Null cell; non T-non B                                              Null_cell
    8       NK cell; natural killer cell (1995+)                                NK_cell                
    L       low grade               Well differentiated; Grade I                G2
    M       intermediate grade      Moderately differentiated; Grade II         G3
    H       high grade              Undifferentiated; anaplastic; Grade IV      G4
    E       “Gleason score 7"       Moderately differentiated; Grade II         G2
    S       sarcomatous overgrowth  Undifferentiated; anaplastic; Grade IV      G4
    
    """
    
    # NAACCR (priority)
    site = get_site(lsplit)
    g_naaccr_clin = None if lsplit[26] == 'Blank(s)' else lsplit[26]
    g_naaccr_path = None if lsplit[27] == 'Blank(s)' else lsplit[27]
    if g_naaccr_path:
        return _cast_naaccrGrade_to_std(g_naaccr_path, site), Source.PATHOLOGICAL
    if g_naaccr_clin:
        return _cast_naaccrGrade_to_std(g_naaccr_clin, site), Source.CLINICAL
    
    # SEER  
    g_seer = None if lsplit[25] == 'Unknown' else lsplit[25]
    if g_seer:
        return _cast_seerGrade_to_std(g_seer), Source.NA

    # No information
    return Grade.NA, Source.NA
    
def _cast_seerGrade_to_std(raw: str) -> Grade:
    return GRADE_SEER_STD_MAP[raw]

def _cast_naaccrGrade_to_std(raw: str, site: str) -> Grade:
    # No G4 Group (no action)
    # Merged G3/G4 Group (no action)
    
    # S Group
    if raw == 'S':
        # if site != 'Corpus Adenosarcoma':
        #     print(f'weird NAACCR grade "S" for site "{site}"')
        # Corpus Adenosarcoma
        # Corpus Uteri
        # Uterus, NOS
        return Grade.G4

    # 8 Group
    if raw == '8':
        return Grade.NA 

    # M Group
    if raw == 'M':
        if site == 'Adrenal Gland':
            return Grade.G4
        elif site == 'Breast':
            return Grade.G3
        else:
            raise RuntimeError

    # B Group
    if raw == 'B':
        return Grade.G2
    
    # E Group
    if raw == 'E':
        assert site == 'Prostate'
        return Grade.G2
    
    return GRADE_NAACCR_STD_MAP[raw]

def get_behavior(lsplit: list[str]) -> Behavior:
    if lsplit[6] == 'Malignant':
        return Behavior.MALIGNANT
    elif lsplit[6] == 'Borderline malignancy':
        return Behavior.BORDERLINE
    elif lsplit[6] in ['Benign', 'In situ']:
        return Behavior.BENIGN
    raise ValueError

def get_brain_met(lsplit: list[str]) -> bool:
    return True if lsplit[7] == 'Yes' else False 

def get_regional_nodes(lsplit: list[str]) -> RegionalNodes:
    the_num = int(lsplit[24])
    if the_num == 0:
        return RegionalNodes.NEG
    elif the_num == 95:
        return RegionalNodes.POS_ASPIRATION
    elif the_num == 98 or the_num == 99:
        return RegionalNodes.NA
    else:
        return RegionalNodes.POS_NODES

def get_malignant_tumors_count(lsplit: list[str]) -> int:
    return 0 if lsplit[20] == 'Unknown' else int(lsplit[20]) 

def get_benign_tumors_count(lsplit: list[str]) -> int:
    return 0 if lsplit[21] == 'Unknown' else int(lsplit[21]) 


if __name__ == '__main__':
    main()


##################
### DEPRECATED ###
##################

def get_tumor_size_dep(lsplit: list[str]) -> Optional[int]: 
    if lsplit[22].isdigit():
        return int(lsplit[22])
    return None



"""
REGIONAL NODES EXAMINED 

00	No nodes were examined
01-89	1-89 nodes were examined (code the exact number of regional lymph nodes examined)
90	90 or more nodes were examined
95	No regional nodes were removed, but aspiration of regional nodes was performed
96	Regional lymph node removal was documented as a sampling, and the number of nodes is unknown/not stated
97	Regional lymph node removal was documented as a dissection, and the number of nodes is unknown/not stated
98	Regional lymph nodes were surgically removed, but the number of lymph nodes is unknown/not stated and not documented as a sampling or dissection; nodes were examined, but the number is unknown
99	It is unknown whether nodes were examined; not stated in patient record
"""

"""
REGIONAL NODES POSITIVE

00	All nodes examined negative.
01-89	1 - 89 nodes positive (code exact number of nodes positive)
90	90 or more nodes positive
95	Positive aspiration or core biopsy of lymph node(s)
97	Positive nodes - number unspecified
98	No nodes examined
99	Unknown if nodes are positive; not applicable. Not documented in patient record
"""

"""

Grade 01
    Lip, Tongue, Gum, Floor, Palate, Buccal, Mouth, Maxillary, Nasal, Larynx, Bile, Gallbladder, Cystic, Bile, Ampulla, Pancreas, Vulva, Vagina, Cervix
    
    Code Grade Description
    1 G1: Well differentiated
    2 G2: Moderately differentiated
    3 G3: Poorly differentiated
    9 Grade cannot be assessed (GX); Unknown
    

Grade 02
    Oropharynx, Hypopharynx, Cutaneous, Small, Colon, Liver, Lung, Pleural, Skin, Conjunctiva

    Code Grade Description
    1 G1: Well differentiated
    2 G2: Moderately differentiated
    3 G3: Poorly differentiated
    4 G4: Undifferentiated
    9 Grade cannot be assessed (GX); Unknown

Grade 03
    Esophagus (including GE junction) Squamous, Esophagus (including GE junction) (excluding Squamous)

    Code Grade Description
    1 G1: Well differentiated
    2 G2: Moderately differentiated
    3 G3: Poorly differentiated, undifferentiated
    9 Grade cannot be assessed (GX); Unknown 

Grade 04
    Stomach

    Code Grade Description
    1 G1: Well differentiated
    2 G2: Moderately differentiated
    3 G3: Poorly differentiated, undifferentiated
    9 Grade cannot be assessed (GX); Unknown 

Grade 05
    Appendix

    1 G1: Well differentiated
    2 G2: Moderately differentiated
    3 G3: Poorly differentiated
    9 Grade cannot be assessed (GX); Unknown 

Grade 07
    NET Stomach, NET Duodenum, NET Ampulla of Vater, NET Jejunum and Ileum, NET Appendix, NET Colon and Rectum, NET Pancreas
    
    Code Grade Description
    1 G1: Stated as WHO Grade 1
    2 G2: Stated as WHO Grade 2
    3 G3: Stated as WHO Grade 3
    A Well differentiated
    B Moderately differentiated
    C Poorly differentiated
    D Undifferentiated, anaplastic
    9 Grade cannot be assessed (GX); Unknown 

Grade 09
    Soft Tissues Head and Neck
    Soft Tissues Abdomen and Thoracic (excluding Heart, Mediastinum, Pleura)
    Heart Mediastinum and Pleura
    Soft Tissue Rare
    Kaposi Sarcoma
    Soft Tissue Other
    Orbital Sarcoma

    Code Grade Description
    1 G1: Stated as FNCLCC Grade 1
    2 G2: Stated as FNCLCC Grade 2
    3 G3: Stated as FNCLCC Grade 3
    A Well differentiated
    B Moderately differentiated
    C Poorly differentiated
    D Undifferentiated, anaplastic
    H Stated as “high grade” only
    9 Grade cannot be assessed (GX); Unknown 

Grade 10
    Soft Tissues Trunk and Extremities, Retroperitoneum

    Code Grade Description
    1 G1: Stated as FNCLCC Grade 1
    2 G2: Stated as FNCLCC Grade 2
    3 G3: Stated as FNCLCC Grade 3
    A Well differentiated
    B Moderately differentiated
    C Poorly differentiated
    D Undifferentiated, anaplastic
    H Stated as “high” grade only
    9 Grade cannot be assessed (GX); Unknown 

Grade 13
    Cervix Sarcoma, Corpus Carcinoma and Carcinosarcoma, Corpus Sarcoma

    Code Grade Description 
    1 G1: FIGO Grade 1 
    2 G2: FIGO Grade 2
    3 G3: FIGO Grade 3
    9 Grade cannot be assessed (GX); Unknown

Grade 14
    Corpus Adenosarcoma 

    Code Grade Description
    1 G1: Well differentiated
    2 G2: Moderately differentiated
    3 G3: Poorly differentiated or undifferentiated
    L Low grade
    H High grade
    S Sarcomatous overgrowth
    9 Grade cannot be assessed (GX); Unknown

Grade 15
    Ovary, Primary Peritoneal Carcinoma, Fallopian Tube

    Code Grade Description
    1 G1: Well differentiated
    2 G2: Moderately differentiated
    3 G3: Poorly differentiated, undifferentiated
    B GB: Borderline Tumor
    L Low grade
    H High grade
    9 Grade cannot be assessed (GX); Unknown 

Grade 19
    Kidney Renal Pelvis, Bladder, Urethra, Urethra-Prostatic

    Code Grade Description
    1 G1: Well differentiated
    2 G2: Moderately differentiated
    3 G3: Poorly differentiated
    L LG: Low-grade
    H HG: High-grade
    9 Grade cannot be assessed (GX); Unknown


Grade 23
    Lymphoma Ocular Adnexa 

    1 G1: 0–5 centroblasts per 10 HPF
    2 G2: 6-15 centroblasts per 10 HPF
    3 G3: More than 15 centroblasts per 10 HPF but with admixed centrocytes
    4 G4: More than 15 centroblasts per 10 HPF but without centrocytes
    9 Grade cannot be assessed (GX); Unknown

Grade 26
    Adrenal Gland 

    Code Grade Description
    L LG: Low grade (<=20 mitosis per 50 HPF)
    H HG: High grade (>20 mitosis per 50 HPF)
    M TP53 or CTNNB Mutation
    A Well differentiated
    B Moderately differentiated
    C Poorly differentiated
    D Undifferentiated, anaplastic
    9 Grade cannot be assessed; Unknown

Grade 88
    Lymphoma, Lymphoma-CLL/SLL, Mycosis Fungoides, Primary Cutaneous Lymphomas (excluding Mycosis Fungoides), Plasma Cell Myeloma, Plasma Cell Disorders, HemeRetic

    Code Grade Description
    8 Not applicable

Grade 98
    Cervical Lymph Nodes and Unknown Primary, Major Salivary Glands, Nasopharynx, Oropharynx HPV-Mediated (p16+), Melanoma Head and Neck, Thymus, Merkel Cell Carcinoma, Melanoma of the Skin, Placenta, Testis, Melanoma Conjunctiva, Thyroid, Thyroid-Medullary, NET Adrenal Gland

    Code Grade Description
    A Well differentiated
    B Moderately differentiated
    C Poorly differentiated
    D Undifferentiated, anaplastic
    9 Grade cannot be assessed; Unknown

Grade 99
    Pharynx Other, Middle Ear, Sinus Other, Biliary Other, Digestive Other, Trachea, Respiratory Other, Skin Other, Adnexa Uterine Other, Genital Female Other, Genital Male Other, Urinary Other, Lacrimal Sac, Eye Other, Endocrine Other, Ill-defined Other

    Code Grade Description
    A Well differentiated
    B Moderately differentiated
    C Poorly differentiated
    D Undifferentiated, anaplastic
    9 Grade cannot be assessed; Unknown

"""


"""
Default Group:
    Codes   Grade Description
    A,1     Well differentiated
    B,2     Moderately differentiated
    C,3     Poorly differentiated
    D,4     Undifferentiated, anaplastic
    9       Grade cannot be assessed; Unknown
    L       Low grade
    H       High grade

    sites
    all (generic)

No G4 Group:
    (4/D (G4) not present)
    Lip, Tongue, Gum, Floor, Palate, Buccal, Mouth, Maxillary, Nasal, Larynx, Bile, Gallbladder, Cystic, Bile, Ampulla, Pancreas, Vulva, Vagina, Cervix;
    Kidney Renal Pelvis, Bladder, Urethra, Urethra-Prostatic;
    Cervix Sarcoma, Corpus Carcinoma and Carcinosarcoma, Corpus Sarcoma;
    Appendix;

S Group:
    (S == Sarcomatous overgrowth)
    Corpus Adenosarcoma 

Merged G3/G4 Group:
    (3 G3: Poorly differentiated or undifferentiated (G3==G4))
    Corpus Adenosarcoma;
    Stomach;
    Esophagus (including GE junction) Squamous, Esophagus (including GE junction) (excluding Squamous);

8 Group: 
    (always 8 - Not applicable)
    Lymphoma, Lymphoma-CLL/SLL, Mycosis Fungoides, Primary Cutaneous Lymphomas (excluding Mycosis Fungoides), Plasma Cell Myeloma, Plasma Cell Disorders, HemeRetic

Adrenal M Group: 
    (M == TP53 or CTNNB Mutation)
    Adrenal Gland

B Group: 
    (B == GB: Borderline Tumor ie map to G2)
    Ovary, Primary Peritoneal Carcinoma, Fallopian Tube
"""

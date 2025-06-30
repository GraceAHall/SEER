
from collections import defaultdict

HISTTYPES_PATH = '/home/grace/work/SEER/data/histology/histcodes.tsv'
SEP_CHAR    = '\t'
ISEP_CHAR   = '|'
NA_CHAR     = '.'

CANCER_PLACEHOLDER = 'other primary'
HISTOLOGY_PLACEHOLDER = 'other histology'
HISTOLOGY_MIN_BRAINMET_OBS = 20
HISTOLOGY_MAX_GROUPS = 3

UNIVERSAL_PREDICTORS = [
    'cancer_group',
    'hist_group',
    'GRADE',
    'TSTAGE',
    'local_ln_met',
    'distant_ln_met',
    'age',
]

UNIVERSAL_NONPREDICTORS = [
    'cancer_type',
    'cancer_group',
    'primary_type',
    'primary_group',
    'hist_type',
    'patient_id',
    'record_number',
    'behavior',
    'COD',
    'diagnosis_year',
    'death_year',
    'survival_months',
    'regional_nodes',
    'brain_met',
    'bone_met',
    'liver_met',
    'lung_met',
    'other_met',
    'any_met',
    'sex',
]


# format: [predictor, use for imputation BOOL]
PREDICTOR_IGNORE_LUT = defaultdict(list)
PREDICTOR_IGNORE_LUT['universal'] += [
    ('NSTAGE', True),
    ('GSTAGE', True),
]
PREDICTOR_IGNORE_LUT['Lung and Bronchus'] += [
    ('pleural_invasion', False),
]
PREDICTOR_IGNORE_LUT['Prostate'] += [
    ('GRADE', False),
]
PREDICTOR_IGNORE_LUT['Breast'] += [
    # ('distant_ln_met', True),
]
PREDICTOR_IGNORE_LUT['Colorectal'] += [
    ('tumor_deposits', False),
    ('perineural_invasion', False),
    ('distant_ln_met', False),
    # 'perineural_invasion',
    # 'distant_ln_met',
]
PREDICTOR_IGNORE_LUT['Esophagus'] += [
    # 'distant_ln_met'
    # 'GRADE',
]
PREDICTOR_IGNORE_LUT['Kidney and Renal Pelvis'] += [
    # 'adrenal_involvement',
    # 'major_vein_involvement',
    # 'capsule_invasion',
    # 'GRADE',
]
PREDICTOR_IGNORE_LUT['Skin'] += [
    ('perineural_invasion', False), 
    ('GRADE', False), 
    ('mitotic_rate', True), 
    ('LDH_elevated_pretreat', False), 
    # ('TSTAGE', True), 
    # ('breslow_thick', True), 
    # ('mitotic_rate', True), 
    # ('ulceration', False), 
    # ('LDH_elevated_pretreat', True), 
]
PREDICTOR_IGNORE_LUT['Pancreas'] += [
    ('GRADE', False),
]
PREDICTOR_IGNORE_LUT['Stomach'] += [
]

# UNIVERSAL_NON_PREDICTORS = [
#     'patient_id',
#     'record_number',
#     'behavior',
#     'COD',
#     'diagnosis_year',
#     'death_year',
#     'survival_months',
#     'cancer_type',
#     'cancer_group',
#     'primary_type',
#     'primary_group',
#     'hist_type',
#     'brain_met',
#     'bone_met',
#     'liver_met',
#     'lung_met',
#     'other_met',
#     'any_met',
# ]

# UNIVERSAL_PREDICTORS_CATEGORICAL = [
#     'sex',
#     'hist_group',
#     'TSTAGE_STD',
#     'NSTAGE_STD',
#     'GSTAGE_STD',
#     'GRADE_STD',
#     # 'regional_nodes',
#     'distant_ln_met',
#     'age', # this needs better binning
# ]

# UNIVERSAL_PREDICTORS_CONTINUOUS = []

# SPECIFIC_PREDICTORS_BOOL = {
#     'Non-Hodgkin Lymphoma': ['B_symptoms'],
#     'Hodgkin Lymphoma': ['B_symptoms'],
#     'Vulva': ['ulceration'],
#     'Skin': ['ulceration'],
# }

# SPECIFIC_PREDICTORS_CATEGORICAL = {
#     'Vulva': ['LDH_pretreatment'],
#     'Breast': ['HER2_type', 'HER2_status'],
    
#     'Ovary': ['ovarian_CA125'],
#     'Non-Hodgkin Lymphoma': ['peripheral_blood_involvement'],
#     'Uterus': ['peritoneal_cytology'],
#     'Skin': ['LDH_pretreatment', 'perineural_invasion'],
#     'Colorectal': ['CEA_pretreat', 'perineural_invasion'],
#     'Lung and Bronchus': ['pleural_invasion'],
#     'Eye and Orbit': ['perineural_invasion'],
#     'Kidney and Renal Pelvis': ['adrenal_involvement', 'major_vein_involvement', 'capsule_invasion'],
#     'Brain': ['chr19q_loh', 'chr1p_loh'],
#     'Cranial Nerves Other Nervous System': ['chr19q_loh', 'chr1p_loh'],
#     'Intrahepatic Bile Duct': ['fibrosis_score'],
#     'Mesothelioma': ['ovarian_CA125', 'pleural_effusion'],
#     'Liver': ['AFP_pretreat_category', 'fibrosis_score'],
#     'Appendix (carcinoid)': ['CEA_pretreat'],
#     'Peritoneum, Omentum and Mesentery': ['ovarian_CA125'],
#     'Appendix (carcinoma)': ['CEA_pretreat'],
#     'Other Digestive Organs': ['ovarian_CA125'],
#     'Testis': ['hGC_post_orchiectomy_elevation', 'LDH_post_orchiectomy_elevation'],
#     'Penis': ['LDH_pretreatment', 'ulceration'],
# }

# SPECIFIC_PREDICTORS_CONTINUOUS = {
#     'Vulva': ['breslow_thick', 'mitotic_rate_melanoma'],
#     'Prostate': ['PSA', 'gleason'],
#     'Skin': ['breslow_thick', 'mitotic_rate_melanoma'],
#     'Colorectal': ['tumor_deposits'],
#     'Testis': ['AFP_post_orchiectomy'],
#     'Penis': ['breslow_thick', 'mitotic_rate_melanoma'],
# }
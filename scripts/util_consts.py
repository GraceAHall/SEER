
HISTTYPES_PATH = '/home/grace/work/SEER/data/histology/histcodes.tsv'
SEP_CHAR    = '\t'
ISEP_CHAR   = '|'
NA_CHAR     = '.'

UNIVERSAL_NON_PREDICTORS = [
    'patient_id',
    'record_number',
    'behavior',
    'COD',
    'diagnosis_year',
    'death_year',
    'survival_months',
    'cancer_type',
    'cancer_group',
    'primary_type',
    'primary_group',
    'hist_type',
    'brain_met',
    'bone_met',
    'liver_met',
    'lung_met',
    'other_met',
    'any_met',
]

UNIVERSAL_PREDICTORS_CATEGORICAL = [
    'sex',
    'hist_group',
    'TSTAGE_STD',
    'NSTAGE_STD',
    'GSTAGE_STD',
    'GRADE_STD',
    # 'regional_nodes',
    'distant_ln_met',
    'age', # this needs better binning
]

UNIVERSAL_PREDICTORS_CONTINUOUS = []

SPECIFIC_PREDICTORS_BOOL = {
    'Non-Hodgkin Lymphoma': ['B_symptoms'],
    'Hodgkin Lymphoma': ['B_symptoms'],
    'Vulva': ['ulceration'],
    'Skin': ['ulceration'],
}

SPECIFIC_PREDICTORS_CATEGORICAL = {
    'Vulva': ['LDH_pretreatment'],
    'Breast': ['HER2_type', 'HER2_status'],
    
    'Ovary': ['ovarian_CA125'],
    'Non-Hodgkin Lymphoma': ['peripheral_blood_involvement'],
    'Uterus': ['peritoneal_cytology'],
    'Skin': ['LDH_pretreatment', 'perineural_invasion'],
    'Colorectal': ['CEA_pretreat', 'perineural_invasion'],
    'Lung and Bronchus': ['pleural_invasion'],
    'Eye and Orbit': ['perineural_invasion'],
    'Kidney and Renal Pelvis': ['adrenal_involvement', 'major_vein_involvement', 'capsule_invasion'],
    'Brain': ['chr19q_loh', 'chr1p_loh'],
    'Cranial Nerves Other Nervous System': ['chr19q_loh', 'chr1p_loh'],
    'Intrahepatic Bile Duct': ['fibrosis_score'],
    'Mesothelioma': ['ovarian_CA125', 'pleural_effusion'],
    'Liver': ['AFP_pretreat_category', 'fibrosis_score'],
    'Appendix (carcinoid)': ['CEA_pretreat'],
    'Peritoneum, Omentum and Mesentery': ['ovarian_CA125'],
    'Appendix (carcinoma)': ['CEA_pretreat'],
    'Other Digestive Organs': ['ovarian_CA125'],
    'Testis': ['hGC_post_orchiectomy_elevation', 'LDH_post_orchiectomy_elevation'],
    'Penis': ['LDH_pretreatment', 'ulceration'],
}

SPECIFIC_PREDICTORS_CONTINUOUS = {
    'Vulva': ['breslow_thick', 'mitotic_rate_melanoma'],
    'Prostate': ['PSA', 'gleason'],
    'Skin': ['breslow_thick', 'mitotic_rate_melanoma'],
    'Colorectal': ['tumor_deposits'],
    'Testis': ['AFP_post_orchiectomy'],
    'Penis': ['breslow_thick', 'mitotic_rate_melanoma'],
}
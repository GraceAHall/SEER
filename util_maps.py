

from util_enums import Grade


###########
# T-STAGE #
###########

TSTAGE_AJCC = set([ 
    'T0', 'T1', 'T1NOS', 'T1a', 'T1a1', 'T1a2', 'T1aNOS', 'T1b', 'T1b1', 'T1b2', 
    'T1bNOS', 'T1c', 'T1mic', 'T2', 'T2NOS', 'T2a', 'T2b', 'T2c', 'T3', 'T3NOS', 
    'T3a', 'T3b', 'T3c', 'T4', 'T4NOS', 'T4a', 'T4b', 'T4c', 'T4d', 'TX', 'Ta', 
    'Tis', 'Tispd', 'Tispu',
])

# https://staging.seer.cancer.gov/cs/input/02.05.50/melanoma_choroid/extension/?breadcrumbs=(~view_schema~,~melanoma_choroid~)
TSTAGE_AJCC7th_AJCC_MAP = {
    'T1 NOS(m)': 'T1NOS',
    'T1 NOS(s)': 'T1NOS', 
    'T1a(m)': 'T1a',
    'T1a(s)': 'T1a',
    'T1b(m)': 'T1b',
    'T1b(s)': 'T1b',
    'T1d': 'T1b',
    'T2(m)': 'T2',
    'T2(s)': 'T2',
    'T2a1': 'T2a',
    'T2a2': 'T2a',
    'T2aNOS': 'T2a',
    'T2d': 'T2b',
    'T3(m)': 'T3',
    'T3(s)': 'T3',
    'T3d': 'T4',
    'T4 NOS(m)': 'T4',
    'T4 NOS(s)': 'T4',
    'T4a(m)': 'T4a',
    'T4a(s)': 'T4a',
    'T4b(m)': 'T4b',
    'T4b(s)': 'T4b',
    'T4e': 'T4'
}

TSTAGE_SEER_AJCC_MAP = {
    'ISU': 'Tispu',
    'ISD': 'Tispd',
    '1MI': 'T1mic',
    '1D': 'T1b',
    '2A1': 'T2a',
    '2A2': 'T2a',
    '2D': 'T2b',
    '3D': 'T4',
    '4E': 'T4',
}

TSTAGE_EOD_AJCC_MAP = {
    'T1b3': 'T1b2',
    'T1c1': 'T1c',
    'T1c2': 'T1c',
    'T1c3': 'T1c',
    'T1d': 'T1b',
    'T1mi': 'T1mic',
    'T2a1': 'T2a',
    'T2a2': 'T2a',
    'T2d': 'T2b',
    'T3d': 'T4',
    'T3e': 'T4',
    'T4e': 'T4',
    'Tis(DCIS)': 'Tis',
    'Tis(LAMN)': 'Tis',
    'Tis(Paget)': 'Tis',
}


###########
# N-STAGE #
###########

NSTAGE_AJCC = set([
    'N0', 'N0(i+)', 'N0(i-)', 'N0(mol+)', 'N0(mol-)', 'N1', 'N1NOS', 'N1a', 
    'N1b', 'N1c', 'N1mi', 'N2', 'N2NOS', 'N2a', 'N2b', 'N2c', 'N3', 'N3NOS', 
    'N3a', 'N3b', 'N3c', 'NX'
])

NSTAGE_SEER_AJCC_MAP = {
    'X': 'NX',
    '0': 'N0',
    '0A': 'N0',
    '0B': 'N0',
    '0I-': 'N0',
    '0I+': 'N0',
    '0M-': 'N0',
    '0M+': 'N0',
    '1': 'N1',
    '1MI': 'N1',
    '1A': 'N1a',
    '1B': 'N1b',
    '1C': 'N1c',
    '2': 'N2',
    '2A': 'N2a',
    '2B': 'N2b',
    '2C': 'N2c',
    '3': 'N3',
    '3A': 'N3a',
    '3B': 'N3b',
    '3C': 'N3c',
    '4': 'N3c',
}

NSTAGE_EOD_AJCC_MAP = {
    'N0a': 'N0',
    'N0b': 'N0',
    'N1a(sn)': 'N1a',
    'N2mi': 'N2',
}

###############
# GROUP-STAGE #
###############

GSTAGE_AJCC = set([
    '0', '0a', '0is', 'I', 'IA', 'IA1', 'IA2', 'IB', 'IB1', 'IB2', 'IC', 'IE', 'IEA', 
    'IEB', 'II', 'IIA', 'IIB', 'IIC', 'IIE', 'IIEA', 'IIEB', 'IIES', 'IIESA', 'IIESB', 
    'III', 'IIIA', 'IIIB', 'IIIC', 'IIIE', 'IIIEA', 'IIIEB', 'IIIES', 'IIIESA', 'IIIESB', 
    'IIINOS', 'IIIS', 'IIISA', 'IIISB', 'IINOS', 'IIS', 'IISA', 'IISB', 'INOS', 'IS', 
    'ISA', 'ISB', 'IV', 'IVA', 'IVB', 'IVC', 'IVNOS', 'OCCULT', 'IIID'
])

GSTAGE_SEER_AJCC_MAP = {
    '0A': '0a', 
    '0IS': '0is', 
    'IIA1': 'IIA', 
    'IIA2': 'IIA', 
    'IIIC1': 'IIIC',
    'IIIC2': 'IIIC', 
    'IVA1': 'IVA', 
    'IVA2': 'IVA', 
    'OC': 'OCCULT', 
}

GSTAGE_EOD_AJCC_MAP = {
    'I:0': 'I',
    'I:2': 'I',
    'I:4': 'I',
    'I:6': 'I',
    'I:5': 'I',
    'I:7': 'I',
    'I:10': 'I',
    'IA3': 'IA2',
    'IB3': 'IB2',
    
    'II bulky': 'II',
    'IIA1': 'IIA',
    'IIA2': 'IIA',
    
    'III:0': 'III',
    'III:2': 'III',
    'III:3': 'III',
    'III:4': 'III',
    'III:5': 'III',
    'III:6': 'III',
    'III:8': 'III',
    'III:9': 'III',
    'III:10': 'III',
    'III:11': 'III',
    'III:13': 'III',
    'III:16': 'III',
    'IIIA1': 'IIIA',
    'IIIA2': 'IIIA',
    'IIIC1': 'IIIC',
    'IIIC2': 'IIIC',

    'IV:5': 'IC',
    'IV:10': 'IC',
    'IV:13': 'IC',
    'IVA1': 'IVA',
    'IVA2': 'IVA',
    
    'OC': 'OCCULT',
}


#########
# GRADE #
#########

GRADE_SEER_STD_MAP = {
    'Well differentiated; Grade I': Grade.G1,
    'Moderately differentiated; Grade II': Grade.G2,
    'Poorly differentiated; Grade III': Grade.G3,
    'Undifferentiated; anaplastic; Grade IV': Grade.G4,
    'T-cell': Grade.T_CELL,
    'B-cell; pre-B; B-precursor': Grade.B_CELL,
    'Null cell; non T-non B': Grade.NULL_CELL,
    'NK cell; natural killer cell (1995+)': Grade.NK_CELL,
}

GRADE_NAACCR_STD_MAP = {
    '1': Grade.G1,
    '2': Grade.G2,
    '3': Grade.G3,
    '4': Grade.G4,
    '5': Grade.T_CELL,
    '6': Grade.B_CELL, 
    '7': Grade.NULL_CELL,
    '8': Grade.NK_CELL,       
    '9': Grade.NA,
    'A': Grade.G1,
    'B': Grade.G2,
    'C': Grade.G3,
    'D': Grade.G4,
    'L': Grade.G2,
    'H': Grade.G4,
}


#########
# SITES #
#########

CANCERTYPE_CANCERGROUP_MAP = {
    
    # Mouth
    'Lip': 'Oral',
    'Tongue': 'Oral',
    'Tonsil': 'Oral',
    'Salivary Gland': 'Oral',
    'Floor of Mouth': 'Oral',
    'Gum and Other Mouth': 'Oral',
    
    # Throat
    'Nasopharynx': 'Throat',
    'Oropharynx': 'Throat',
    'Hypopharynx': 'Throat',

    # Colorectal
    'Ascending Colon': 'Colorectal',
    'Cecum': 'Colorectal',
    'Hepatic Flexure': 'Colorectal',
    'Transverse Colon': 'Colorectal',
    'Splenic Flexure': 'Colorectal',
    'Descending Colon': 'Colorectal',
    'Sigmoid Colon': 'Colorectal',
    'Large Intestine, NOS': 'Colorectal',
    'Rectosigmoid Junction': 'Colorectal',
    'Rectum': 'Colorectal',

    # Skin
    'Melanoma of the Skin': 'Skin',
    'Other Non-Epithelial Skin': 'Skin',

    # leukemia
    'Myeloma': 'Leukemia',
    'Acute Lymphocytic Leukemia': 'Leukemia',
    'Acute Monocytic Leukemia': 'Leukemia',
    'Acute Myeloid Leukemia': 'Leukemia',
    'Aleukemic, Subleukemic and NOS': 'Leukemia',
    'Chronic Lymphocytic Leukemia': 'Leukemia',
    'Chronic Myeloid Leukemia': 'Leukemia',
    'Other Acute Leukemia': 'Leukemia',
    'Other Myeloid/Monocytic Leukemia': 'Leukemia',
    'Other Lymphocytic Leukemia': 'Leukemia',

    # female genitals
    'Cervix Uteri': 'Cervix',
    'Corpus Uteri': 'Uterus',
    'Uterus, NOS': 'Uterus',

    # lymphomas
    'Hodgkin - Extranodal': 'Hodgkin Lymphoma',
    'Hodgkin - Nodal': 'Hodgkin Lymphoma',
    'NHL - Extranodal': 'Non-Hodgkin Lymphoma',
    'NHL - Nodal': 'Non-Hodgkin Lymphoma',
    
    # CNS
    'Brain': 'CNS',
    'Cranial Nerves Other Nervous System': 'CNS',
    
    # unchanged
    'Trachea, Mediastinum and Other Respiratory Organs': 'Trachea, Mediastinum and Other Respiratory Organs',
    'Anus, Anal Canal and Anorectum': 'Anus, Anal Canal and Anorectum',
    'Appendix': 'Appendix',
    'Bones and Joints': 'Bones and Joints',
    'Breast': 'Breast',
    'Esophagus': 'Esophagus',
    'Eye and Orbit': 'Eye and Orbit',
    'Gallbladder': 'Gallbladder',
    'Intrahepatic Bile Duct': 'Intrahepatic Bile Duct',
    'Kaposi Sarcoma': 'Kaposi Sarcoma',
    'Kidney and Renal Pelvis': 'Kidney and Renal Pelvis',
    'Larynx': 'Larynx',
    'Liver': 'Liver',
    'Lung and Bronchus': 'Lung and Bronchus',
    'Mesothelioma': 'Mesothelioma',
    'Nose, Nasal Cavity and Middle Ear': 'Nose, Nasal Cavity and Middle Ear',
    'Ovary': 'Ovary',
    'Pancreas': 'Pancreas',
    'Penis': 'Penis',
    'Peritoneum, Omentum and Mesentery': 'Peritoneum, Omentum and Mesentery',
    'Pleura': 'Pleura',
    'Prostate': 'Prostate',
    'Retroperitoneum': 'Retroperitoneum',
    'Small Intestine': 'Small Intestine',
    'Soft Tissue including Heart': 'Soft Tissue including Heart',
    'Stomach': 'Stomach',
    'Testis': 'Testis',
    'Thyroid': 'Thyroid',
    'Ureter': 'Ureter',
    'Urinary Bladder': 'Urinary Bladder',
    'Vagina': 'Vagina',
    'Vulva': 'Vulva',
    'Other Oral Cavity and Pharynx': 'Other Oral Cavity and Pharynx',
    'Other Biliary': 'Other Biliary',
    'Other Digestive Organs': 'Other Digestive Organs',
    'Other Endocrine including Thymus': 'Other Endocrine including Thymus',
    'Other Female Genital Organs': 'Other Female Genital Organs',
    'Other Male Genital Organs': 'Other Male Genital Organs',
    'Other Urinary Organs': 'Other Urinary Organs',
    'Miscellaneous': 'Miscellaneous',

}


PRIMARYCODE_PRIMARYSITE_MAP = {
    24: 'Tongue | Lymphatics',
    98: 'Tonsil | Lymphatics',
    99: 'Tonsil | Lymphatics',
    111: 'Nasopharynx | Lymphatics',
    129: 'Hypopharynx',
    140: 'Other Oral Cavity and Pharynx',
    142: 'Other Oral Cavity and Pharynx | Lymphatics',
    148: 'Other Oral Cavity and Pharynx',
    180: 'Cecum',
    181: 'Appendix',
    182: 'Ascending Colon',
    183: 'Hepatic Flexure',
    184: 'Transverse Colon',
    185: 'Splenic Flexure',
    186: 'Descending Colon',
    187: 'Sigmoid Colon',
    188: 'Large Intestine, NOS',
    189: 'Large Intestine, NOS',
    199: 'Rectosigmoid Junction',
    209: 'Rectum',
    210: 'Anus, Anal Canal and Anorectum',
    211: 'Anus, Anal Canal and Anorectum',
    212: 'Anus, Anal Canal and Anorectum',
    218: 'Anus, Anal Canal and Anorectum',
    220: 'Liver',
    221: 'Intrahepatic Bile Duct',
    239: 'Gallbladder',
    260: 'Large Intestine, NOS',
    268: 'Other Digestive Organs',
    269: 'Other Digestive Organs',
    300: 'Nose, Nasal Cavity and Middle Ear',
    301: 'Nose, Nasal Cavity and Middle Ear',
    339: 'Trachea, Mediastinum and Other Respiratory Organs',
    379: 'Other Endocrine including Thymus | Lymphatics',
    380: 'Soft Tissue including Heart',
    381: 'Trachea, Mediastinum and Other Respiratory Organs',
    382: 'Trachea, Mediastinum and Other Respiratory Organs',
    383: 'Trachea, Mediastinum and Other Respiratory Organs',
    384: 'Pleura',
    388: 'Trachea, Mediastinum and Other Respiratory Organs',
    390: 'Trachea, Mediastinum and Other Respiratory Organs',
    398: 'Trachea, Mediastinum and Other Respiratory Organs',
    399: 'Trachea, Mediastinum and Other Respiratory Organs',
    420: 'Lymphatics | Miscellaneous',
    421: 'Lymphatics | Miscellaneous',
    422: 'Lymphatics | Miscellaneous',
    423: 'Miscellaneous',
    424: 'Lymphatics | Miscellaneous',
    480: 'Retroperitoneum',
    481: 'Peritoneum, Omentum and Mesentery',
    482: 'Peritoneum, Omentum and Mesentery',
    488: 'Other Digestive Organs',
    529: 'Vagina',
    559: 'Uterus, NOS',
    569: 'Ovary',
    589: 'Other Female Genital Organs',
    619: 'Prostate',
    649: 'Kidney and Renal Pelvis',
    659: 'Kidney and Renal Pelvis',
    669: 'Ureter',
    739: 'Thyroid',
    809: 'Miscellaneous',
}

PRIMARYCODE_PRIMARYSITE_RANGES = [
    (0, 9, 'Lip'),
    (19, 29, 'Tongue'),
    (40, 49, 'Floor of Mouth'),
    (30, 39, 'Gum and Other Mouth'),
    (50, 59, 'Gum and Other Mouth'),
    (60, 69, 'Gum and Other Mouth'),
    (79, 89, 'Salivary Gland'),
    (90, 99, 'Tonsil'),
    (100, 109, 'Oropharynx'),
    (110, 119, 'Nasopharynx'),
    (130, 139, 'Hypopharynx'),
    (150, 159, 'Esophagus'),
    (160, 169, 'Stomach'),
    (170, 179, 'Small Intestine'),
    (240, 249, 'Other Biliary'),
    (250, 259, 'Pancreas'),
    (310, 319, 'Nose, Nasal Cavity and Middle Ear'),
    (320, 329, 'Larynx'),
    (340, 349, 'Lung and Bronchus'),
    (400, 419, 'Bones and Joints'),
    (440, 449, 'Melanoma of the Skin | Other Non-Epithelial Skin'),
    (470, 479, 'Soft Tissue including Heart'),
    (490, 499, 'Soft Tissue including Heart'),
    (500, 509, 'Breast'),
    (510, 519, 'Vulva'),
    (530, 539, 'Cervix Uteri'),
    (540, 549, 'Corpus Uteri'),
    (570, 579, 'Other Female Genital Organs'),
    (600, 609, 'Penis'),
    (620, 629, 'Testis'),
    (630, 639, 'Other Male Genital Organs'),
    (670, 679, 'Urinary Bladder'),
    (680, 689, 'Other Urinary Organs'),
    (690, 699, 'Eye and Orbit'),
    (700, 709, 'Cranial Nerves Other Nervous System'),
    (710, 719, 'Brain | Cranial Nerves Other Nervous System'),
    (720, 729, 'Cranial Nerves Other Nervous System'),
    (740, 749, 'Other Endocrine including Thymus'),
    (750, 759, 'Other Endocrine including Thymus'),
    (760, 768, 'Miscellaneous'),
    (770, 779, 'Lymphatics | Miscellaneous'),
]

CGROUPS_NSTAGES_N0N1N2N3 = {
    'Anus, Anal Canal and Anorectum',
    'Breast',
    'Esophagus',
    'Kaposi Sarcoma',
    'Leukemia',
    'Lung and Bronchus',
    'Mesothelioma',
    'Miscellaneous',
    'Nose, Nasal Cavity and Middle Ear',
    'Oral',
    'Other Digestive Organs',
    'Other Male Genital Organs',
    'Other Oral Cavity and Pharynx',
    'Pleura',
    'Skin',
    'Stomach',
    'Testis',
    'Throat',
    'Trachea, Mediastinum and Other Respiratory Organs',
    'Urinary Bladder',
    'Vulva',
    'Larynx',
    'Penis',
    'Ureter',
}

CGROUPS_NSTAGES_N0N1N2 = {
    'Other Urinary Organs',
    'Kidney and Renal Pelvis',
    'Other Endocrine including Thymus',
    'Uterus',
    'Colorectal',
    'Gallbladder',
    'Small Intestine',
    'Appendix (carcinoma)',
    'Corpus Uteri (carcinoma)',
}

CGROUPS_NSTAGES_N0N1 = {
    'Other Female Genital Organs',
    'Soft Tissue including Heart',
    'Thyroid',
    'Eye and Orbit',
    'Prostate',
    'Bones and Joints',
    'Cervix',
    'Retroperitoneum',
    'Vagina',
    'Liver',
    'Ovary',
    'Intrahepatic Bile Duct',
    'Pancreas',                 # AJCC 7th page 257
    'Other Biliary',
    'Appendix (carcinoid)',
    'Corpus Uteri (sarcoma)',
}

WEIRD_NSTAGES = {
    'Peritoneum, Omentum and Mesentery', # ???
}

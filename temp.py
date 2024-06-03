
NSTAGE_STD = set([
    'N0', 'N0(i+)', 'N0(i-)', 'N0(mol+)', 'N0(mol-)', 'N1', 'N1NOS', 'N1a', 
    'N1b', 'N1c', 'N1mi', 'N2', 'N2NOS', 'N2a', 'N2b', 'N2c', 'N3', 'N3NOS', 
    'N3a', 'N3b', 'N3c', 'NA', 'NX'
])

NSTAGE_EOD = set([
    'N0', 'N0(i+)', 'N0(mol+)', 'N0a', 'N0b', 'N1', 'N1a', 'N1a(sn)', 'N1b', 
    'N1c', 'N1mi', 'N2', 'N2a', 'N2b', 'N2c', 'N2mi', 'N3', 'N3a', 'N3b', 'N3c', 'NX'
])

print('NSTAGE EOD UNIQUE')
print(NSTAGE_EOD - NSTAGE_STD)

GSTAGE_STD = set([
    '0', '0a', '0is', 'I', 'IA', 'IA1', 'IA2', 'IB', 'IB1', 'IB2', 'IC', 'IE', 'IEA', 
    'IEB', 'II', 'IIA', 'IIB', 'IIC', 'IIE', 'IIEA', 'IIEB', 'IIES', 'IIESA', 'IIESB', 
    'III', 'IIIA', 'IIIB', 'IIIC', 'IIIE', 'IIIEA', 'IIIEB', 'IIIES', 'IIIESA', 'IIIESB', 
    'IIINOS', 'IIIS', 'IIISA', 'IIISB', 'IINOS', 'IIS', 'IISA', 'IISB', 'INOS', 'IS', 
    'ISA', 'ISB', 'IV', 'IVA', 'IVB', 'IVC', 'IVNOS', 'OCCULT'
])
GSTAGE_SEER = set([
    '0', '0A', '0IS', 'I', 'IA', 'IA1', 'IA2', 'IB', 'IB1', 'IB2', 'IC', 'IS', 'II', 
    'IIA', 'IIA1', 'IIA2', 'IIB', 'IIC', 'III', 'IIIA', 'IIIB', 'IIIC', 'IIIC1', 'IIIC2', 'IV', 'IVA', 
    'IVA1', 'IVA2', 'IVB', 'IVC', '99', 'OC'
])
GSTAGE_EOD = set([
    '0', '0a', '0is', 'I', 'I:0', 'I:10', 'I:2', 'I:4', 'I:5', 'I:6', 'I:7', 'IA', 
    'IA1', 'IA2', 'IA3', 'IB', 'IB1', 'IB2', 'IB3', 'IC', 'IE', 'IS', 'II', 'II bulky', 
    'IIA', 'IIA1', 'IIA2', 'IIB', 'IIC', 'IIE', 'III', 'III:0', 'III:10', 'III:11', 'III:13', 'III:16', 
    'III:2', 'III:3', 'III:4', 'III:5', 'III:6', 'III:8', 'III:9', 'IIIA', 'IIIA1', 'IIIA2', 'IIIB', 'IIIC', 
    'IIIC1', 'IIIC2', 'IIID', 'IV', 'IV:10', 'IV:13', 'IV:5', 'IVA', 'IVA1', 'IVA2', 'IVB', 'IVC', 
    '88', '99', 'OC'
])

print('GSTAGE SEER UNIQUE')
print(GSTAGE_SEER - GSTAGE_STD)

print('GSTAGE EOD UNIQUE')
print(GSTAGE_EOD - GSTAGE_STD)
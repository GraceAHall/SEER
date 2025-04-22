
import sys

INFILE = sys.argv[1]
OUTFILE = sys.argv[2]

with open(INFILE, 'r') as infp:
    with open(OUTFILE, 'w') as outfp:
        for line in infp.readlines():
            if 'Age-Standardized Life' in line:
                lsplit = line.split('\t')
                outfp.write('\t'.join(lsplit[2:]))

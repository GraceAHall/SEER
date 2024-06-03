
# counts by site
cut -f6 /home/grace/work/brainmets/SEER/BrainMetsQueryFull.txt | sort | uniq -c

# counts by site for brainmet=True
awk -F'\t' '$8 == "Yes" {print $0}' /home/grace/work/brainmets/SEER/BrainMetsQueryFull.sample.txt | cut -f6 | sort | uniq -c

awk -F'\t' '$8 == "No" && $6 == "Brain" {print $0}' /home/grace/work/brainmets/SEER/BrainMetsQueryFull.sample.txt
#!/bin/bash
# knucleotide.sh - Minimal k-nucleotide counter using awk/sed
set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <fasta_file>"
    exit 1
fi

FASTA="$1"
TMP_SEQ=$(mktemp)

# Extract sequence after >THREE
awk '/^>THREE/{flag=1; next} /^>/{flag=0} flag && !/^$/ {print}' "$FASTA" | \
    tr -d '\n\r' | tr '[:lower:]' '[:upper:]' > "$TMP_SEQ"

SEQUENCE=$(cat "$TMP_SEQ")
LEN=${#SEQUENCE}

echo "Sequence length: $LEN"
echo ""

# Count single nucleotides
echo "Single nucleotide counts:"
for BASE in A C G T; do
    COUNT=$(grep -o "$BASE" <<< "$SEQUENCE" | wc -l)
    PERCENT=$(echo "scale=2; $COUNT * 100 / $LEN" | bc)
    echo "$BASE: $COUNT ($PERCENT%)"
done

echo ""
echo "Most frequent 4-mers:"
# Extract all 4-mers and count
for ((i=0; i<=LEN-4; i++)); do
    echo "${SEQUENCE:i:4}"
done | sort | uniq -c | sort -rn | head -7 | \
    awk '{printf "%s\t%d\t%.3f%%\n", $2, $1, $1/(NR>1?LEN-3:LEN-3)*100}' LEN="$LEN"

rm "$TMP_SEQ"
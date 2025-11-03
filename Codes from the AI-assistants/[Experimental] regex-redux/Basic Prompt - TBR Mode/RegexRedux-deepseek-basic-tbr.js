const fs = require('fs');

const input = fs.readFileSync(0, 'utf-8'); // Read entire stdin
const ilen = input.length;

// Remove FASTA header and newlines
let cleaned = input.replace(/>.*\n|\n/g, '');
const clen = cleaned.length;

// Patterns for counting
const patterns = [
    "agggtaaa|tttaccct",
    "[cgt]gggtaaa|tttaccc[acg]",
    "a[act]ggtaaa|tttacc[agt]t",
    "ag[act]gtaaa|tttac[agt]ct",
    "agg[act]taaa|ttta[agt]cct",
    "aggg[acg]aaa|ttt[cgt]ccct",
    "agggt[cgt]aa|tt[acg]accct",
    "agggta[cgt]a|t[acg]taccct",
    "agggtaa[cgt]|[acg]ttaccct"
];

// Count occurrences for each pattern
const counts = [];
patterns.forEach(p => {
    const re = new RegExp(p, 'gi');
    const matches = cleaned.match(re);
    counts.push(matches ? matches.length : 0);
    console.log(`${p} ${counts[counts.length - 1]}`);
});

console.log(''); // Blank line
console.log(ilen);
console.log(clen);

// IUB replacements
const iubMap = {
    'B': '(c|g|t)',
    'D': '(a|g|t)',
    'H': '(a|c|t)',
    'K': '(g|t)',
    'M': '(a|c)',
    'N': '(a|c|g|t)',
    'R': '(a|g)',
    'S': '(c|g)',
    'V': '(a|c|g)',
    'W': '(a|t)',
    'Y': '(c|t)'
};
const iubRegex = new RegExp(`[${Object.keys(iubMap).join('')}]`, 'g');
const iubStr = cleaned.replace(iubRegex, match => iubMap[match]);
const iubLen = iubStr.length;

console.log(iubLen);
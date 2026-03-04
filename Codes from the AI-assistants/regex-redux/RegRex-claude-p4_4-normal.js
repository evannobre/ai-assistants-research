#!/usr/bin/env node
/**
 * Regex-Redux: FASTA sequence processing benchmark
 * Uses native regex capabilities
 */

const fs = require('fs');

// Read all input from stdin
let inputData = fs.readFileSync(0, 'utf-8');

const initialLength = inputData.length;

// Remove FASTA descriptions and linefeeds
const sequence = inputData.replace(/>.*\n|\n/g, '');
const cleanedLength = sequence.length;

// Define the 8-mer patterns
const patterns = [
    /agggtaaa|tttaccct/g,
    /[cgt]gggtaaa|tttaccc[acg]/g,
    /a[act]ggtaaa|tttacc[agt]t/g,
    /ag[act]gtaaa|tttac[agt]ct/g,
    /agg[act]taaa|ttta[agt]cct/g,
    /aggg[acg]aaa|ttt[cgt]ccct/g,
    /agggt[cgt]aa|tt[acg]accct/g,
    /agggta[cgt]a|t[acg]taccct/g,
    /agggtaa[cgt]|[acg]ttaccct/g
];

const patternStrings = [
    'agggtaaa|tttaccct',
    '[cgt]gggtaaa|tttaccc[acg]',
    'a[act]ggtaaa|tttacc[agt]t',
    'ag[act]gtaaa|tttac[agt]ct',
    'agg[act]taaa|ttta[agt]cct',
    'aggg[acg]aaa|ttt[cgt]ccct',
    'agggt[cgt]aa|tt[acg]accct',
    'agggta[cgt]a|t[acg]taccct',
    'agggtaa[cgt]|[acg]ttaccct'
];

// Count matches for each pattern
for (let i = 0; i < patterns.length; i++) {
    const matches = sequence.match(patterns[i]);
    const count = matches ? matches.length : 0;
    console.log(`${patternStrings[i]} ${count}`);
}

// Define magic patterns and replacements
const replacements = [
    { pattern: /tHa[Nt]/g, replacement: '<4>' },
    { pattern: /aND|caN|Ha[DS]|WaS/g, replacement: '<3>' },
    { pattern: /a[NSt]|BY/g, replacement: '<2>' },
    { pattern: /<[^>]*>/g, replacement: '|' },
    { pattern: /\|[^|][^|]*\|/g, replacement: '-' }
];

// Apply replacements one at a time
let resultSequence = sequence;
for (const { pattern, replacement } of replacements) {
    resultSequence = resultSequence.replace(pattern, replacement);
}

const finalLength = resultSequence.length;

// Write the three recorded sequence lengths
console.log();
console.log(initialLength);
console.log(cleanedLength);
console.log(finalLength);
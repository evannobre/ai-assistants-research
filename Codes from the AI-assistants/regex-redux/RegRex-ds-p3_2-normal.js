const fs = require('fs');
const readline = require('readline');

async function main() {
    // Read all input from stdin
    const input = fs.readFileSync(0, 'utf8');
    
    // Record initial length
    const initialLength = input.length;
    
    // 1. Remove FASTA sequence descriptions and linefeeds
    let cleaned = input.replace(/>.*\n|\n/g, '');
    
    // Record cleaned length
    const cleanedLength = cleaned.length;
    
    // 2. Count patterns
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
    
    patterns.forEach(pattern => {
        const matches = cleaned.match(pattern);
        const count = matches ? matches.length : 0;
        console.log(`${pattern.source} ${count}`);
    });
    
    // 3. Apply substitution patterns
    const substitutions = [
        [/tHa[Nt]/g, "<4>"],
        [/aND|caN|Ha[DS]|WaS/g, "<3>"],
        [/a[NSt]|BY/g, "<2>"],
        /<[^>]*>/g,
        /\\|[^|][^|]*\\|/g
    ];
    
    let transformed = cleaned;
    
    // First three substitutions
    for (let i = 0; i < 3; i++) {
        transformed = transformed.replace(substitutions[i][0], substitutions[i][1]);
    }
    
    // Fourth substitution: <[^>]*> -> |
    transformed = transformed.replace(substitutions[3][0], '|');
    
    // Fifth substitution: \|[^|][^|]*\| -> -
    transformed = transformed.replace(substitutions[4][0], '-');
    
    // Record final length
    const finalLength = transformed.length;
    
    // 4. Print lengths
    console.log(`\n${initialLength}\n${cleanedLength}\n${finalLength}`);
}

// Handle async main
if (require.main === module) {
    main().catch(console.error);
}
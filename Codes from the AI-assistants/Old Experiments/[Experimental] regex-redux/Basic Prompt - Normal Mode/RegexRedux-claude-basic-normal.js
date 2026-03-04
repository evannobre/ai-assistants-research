#!/usr/bin/env node
/**
 * Regex Redux Algorithm Implementation in JavaScript
 * Uses native Node.js modules for maximum performance
 */

const fs = require('fs');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const os = require('os');

// Worker function for parallel pattern matching
if (!isMainThread) {
    const { sequence, pattern } = workerData;
    const regex = new RegExp(pattern, 'gi');
    const matches = sequence.match(regex);
    parentPort.postMessage(matches ? matches.length : 0);
    process.exit(0);
}

async function regexReduxSolution() {
    // Read input from stdin
    let input = '';
    
    return new Promise((resolve) => {
        process.stdin.setEncoding('utf8');
        
        process.stdin.on('data', (chunk) => {
            input += chunk;
        });
        
        process.stdin.on('end', async () => {
            const originalLength = input.length;
            
            // Step 1: Remove sequence descriptions and newlines
            const sequence = input.replace(/>.*\n|\n/g, '');
            const cleanedLength = sequence.length;
            
            // Step 2: Define patterns to count
            const patterns = [
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
            
            // Step 3: Count patterns using Worker threads for parallel processing
            const counts = await countPatternsParallel(sequence, patterns);
            
            // Step 4: Apply replacements
            const replacements = [
                [/tHa[Nt]/gi, '<4>'],
                [/aND|caN|Ha[DS]|WaS/gi, '<3>'],
                [/a[NSt]|BY/gi, '<2>'],
                [/<[^>]*>/g, '|'],
                [/\|[^|][^|]*\|/g, '-']
            ];
            
            let resultSequence = sequence;
            for (const [pattern, replacement] of replacements) {
                resultSequence = resultSequence.replace(pattern, replacement);
            }
            
            const finalLength = resultSequence.length;
            
            // Output results
            patterns.forEach((pattern, i) => {
                console.log(`${pattern} ${counts[i]}`);
            });
            
            console.log(`\n${originalLength}`);
            console.log(`${cleanedLength}`);
            console.log(`${finalLength}`);
            
            resolve();
        });
    });
}

async function countPatternsParallel(sequence, patterns) {
    const numWorkers = Math.min(patterns.length, os.cpus().length);
    const promises = [];
    
    for (let i = 0; i < patterns.length; i++) {
        const promise = new Promise((resolve, reject) => {
            const worker = new Worker(__filename, {
                workerData: { sequence, pattern: patterns[i] }
            });
            
            worker.on('message', resolve);
            worker.on('error', reject);
        });
        promises.push(promise);
    }
    
    return Promise.all(promises);
}

// Optimized synchronous version
function optimizedRegexRedux() {
    const input = fs.readFileSync(0, 'utf8');
    const originalLength = input.length;
    
    // Pre-compile cleanup regex
    const cleanupRegex = />.*\n|\n/g;
    const sequence = input.replace(cleanupRegex, '');
    const cleanedLength = sequence.length;
    
    // Pre-compile counting patterns
    const countPatterns = [
        /agggtaaa|tttaccct/gi,
        /[cgt]gggtaaa|tttaccc[acg]/gi,
        /a[act]ggtaaa|tttacc[agt]t/gi,
        /ag[act]gtaaa|tttac[agt]ct/gi,
        /agg[act]taaa|ttta[agt]cct/gi,
        /aggg[acg]aaa|ttt[cgt]ccct/gi,
        /agggt[cgt]aa|tt[acg]accct/gi,
        /agggta[cgt]a|t[acg]taccct/gi,
        /agggtaa[cgt]|[acg]ttaccct/gi
    ];
    
    // Count patterns efficiently
    const counts = countPatterns.map(pattern => {
        const matches = sequence.match(pattern);
        return matches ? matches.length : 0;
    });
    
    // Pre-compile replacement patterns
    const replacements = [
        [/tHa[Nt]/gi, '<4>'],
        [/aND|caN|Ha[DS]|WaS/gi, '<3>'],
        [/a[NSt]|BY/gi, '<2>'],
        [/<[^>]*>/g, '|'],
        [/\|[^|][^|]*\|/g, '-']
    ];
    
    // Apply replacements
    let resultSequence = sequence;
    replacements.forEach(([pattern, replacement]) => {
        resultSequence = resultSequence.replace(pattern, replacement);
    });
    
    const finalLength = resultSequence.length;
    
    // Output results
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
    
    patternStrings.forEach((pattern, i) => {
        console.log(`${pattern} ${counts[i]}`);
    });
    
    console.log(`\n${originalLength}`);
    console.log(`${cleanedLength}`);
    console.log(`${finalLength}`);
}

// Stream-based version for large files
function streamBasedRegexRedux() {
    const readline = require('readline');
    
    const rl = readline.createInterface({
        input: process.stdin,
        crlfDelay: Infinity
    });
    
    let sequence = '';
    let originalLength = 0;
    
    rl.on('line', (line) => {
        originalLength += line.length + 1; // +1 for newline
        if (!line.startsWith('>')) {
            sequence += line;
        }
    });
    
    rl.on('close', () => {
        originalLength -= 1; // Adjust for last newline
        const cleanedLength = sequence.length;
        
        // Process patterns
        const patterns = [
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
        
        const counts = patterns.map(pattern => {
            const regex = new RegExp(pattern, 'gi');
            const matches = sequence.match(regex);
            return matches ? matches.length : 0;
        });
        
        // Apply replacements
        let result = sequence
            .replace(/tHa[Nt]/gi, '<4>')
            .replace(/aND|caN|Ha[DS]|WaS/gi, '<3>')
            .replace(/a[NSt]|BY/gi, '<2>')
            .replace(/<[^>]*>/g, '|')
            .replace(/\|[^|][^|]*\|/g, '-');
        
        const finalLength = result.length;
        
        // Output
        patterns.forEach((pattern, i) => {
            console.log(`${pattern} ${counts[i]}`);
        });
        
        console.log(`\n${originalLength}`);
        console.log(`${cleanedLength}`);
        console.log(`${finalLength}`);
    });
}

// Main execution
if (isMainThread) {
    // Choose implementation based on your needs:
    optimizedRegexRedux();        // Best for most cases
    // regexReduxSolution();      // Parallel processing version
    // streamBasedRegexRedux();   // Memory-efficient streaming version
}
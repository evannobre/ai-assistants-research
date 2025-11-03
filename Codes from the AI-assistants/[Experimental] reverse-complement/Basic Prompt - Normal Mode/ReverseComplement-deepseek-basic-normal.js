function reverseComplement(dna) {
    const complement = {'A':'T', 'T':'A', 'C':'G', 'G':'C', 'a':'t', 't':'a', 'c':'g', 'g':'c'};
    return dna.split('').reverse().map(base => complement[base]).join('');
}

const dna = process.argv[2];
console.log(`Original: ${dna}`);
console.log(`Reverse complement: ${reverseComplement(dna)}`);
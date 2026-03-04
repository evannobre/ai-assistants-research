use std::io::{self, Read};
use regex::Regex;

fn main() {
    // Read all input from stdin
    let mut input_data = String::new();
    io::stdin().read_to_string(&mut input_data)
        .expect("Failed to read from stdin");
    
    let initial_length = input_data.len();
    
    // Remove FASTA descriptions and linefeeds
    let re = Regex::new(r">.*\n|\n").unwrap();
    let sequence = re.replace_all(&input_data, "");
    let cleaned_length = sequence.len();
    
    // Define the 8-mer patterns
    let patterns = vec![
        r"agggtaaa|tttaccct",
        r"[cgt]gggtaaa|tttaccc[acg]",
        r"a[act]ggtaaa|tttacc[agt]t",
        r"ag[act]gtaaa|tttac[agt]ct",
        r"agg[act]taaa|ttta[agt]cct",
        r"aggg[acg]aaa|ttt[cgt]ccct",
        r"agggt[cgt]aa|tt[acg]accct",
        r"agggta[cgt]a|t[acg]taccct",
        r"agggtaa[cgt]|[acg]ttaccct",
    ];
    
    // Count matches for each pattern
    for pattern in &patterns {
        let re = Regex::new(pattern).unwrap();
        let count = re.find_iter(&sequence).count();
        println!("{} {}", pattern, count);
    }
    
    // Define magic patterns and replacements
    let replacements = vec![
        (r"tHa[Nt]", "<4>"),
        (r"aND|caN|Ha[DS]|WaS", "<3>"),
        (r"a[NSt]|BY", "<2>"),
        (r"<[^>]*>", "|"),
        (r"\|[^|][^|]*\|", "-"),
    ];
    
    // Apply replacements one at a time
    let mut result_sequence = sequence.to_string();
    for (pattern, replacement) in &replacements {
        let re = Regex::new(pattern).unwrap();
        result_sequence = re.replace_all(&result_sequence, *replacement).to_string();
    }
    
    let final_length = result_sequence.len();
    
    // Write the three recorded sequence lengths
    println!();
    println!("{}", initial_length);
    println!("{}", cleaned_length);
    println!("{}", final_length);
}
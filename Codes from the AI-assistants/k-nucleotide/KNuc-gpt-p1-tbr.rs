use std::collections::HashMap;
use std::io::{self, BufRead};

fn base_to_2bit(b: u8) -> Option<u8> {
    match b {
        b'A' | b'a' => Some(0),
        b'C' | b'c' => Some(1),
        b'G' | b'g' => Some(2),
        b'T' | b't' | b'U' | b'u' => Some(3),
        _ => None, // ignore anything else (newlines, ambiguous codes, etc.)
    }
}

fn encode_kmer_to_string(mut code: u64, k: usize) -> String {
    let mut out = vec![b'A'; k];
    for i in (0..k).rev() {
        let v = (code & 0b11) as u8;
        out[i] = match v {
            0 => b'A',
            1 => b'C',
            2 => b'G',
            _ => b'T',
        };
        code >>= 2;
    }
    String::from_utf8(out).unwrap()
}

fn encode_pattern(pat: &str) -> u64 {
    let mut code: u64 = 0;
    for &b in pat.as_bytes() {
        let v = base_to_2bit(b).expect("Pattern contains non-ACGT base");
        code = (code << 2) | v as u64;
    }
    code
}

fn count_k(seq2: &[u8], k: usize) -> HashMap<u64, u32> {
    let mut map: HashMap<u64, u32> = HashMap::new();
    if k == 0 || seq2.len() < k {
        return map;
    }

    let mask: u64 = if 2 * k == 64 {
        u64::MAX
    } else {
        (1u64 << (2 * k)) - 1
    };

    let mut code: u64 = 0;

    // prime first k bases
    for i in 0..k {
        code = (code << 2) | (seq2[i] as u64);
    }
    *map.entry(code).or_insert(0) += 1;

    // rolling window
    for &b in &seq2[k..] {
        code = ((code << 2) | (b as u64)) & mask;
        *map.entry(code).or_insert(0) += 1;
    }

    map
}

fn print_freq(seq2: &[u8], k: usize) {
    let map = count_k(seq2, k);
    let total = (seq2.len().saturating_sub(k) + 1) as f64;

    let mut items: Vec<(String, u32)> = map
        .into_iter()
        .map(|(code, cnt)| (encode_kmer_to_string(code, k), cnt))
        .collect();

    // sort: count desc, key asc
    items.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));

    for (kmer, cnt) in items {
        let pct = (cnt as f64) * 100.0 / total;
        println!("{} {:.3}", kmer, pct);
    }
    println!();
}

fn main() {
    // 1) Read FASTA line-by-line, extract sequence for >THREE
    let stdin = io::stdin();
    let mut reader = stdin.lock().lines();

    let mut in_three = false;
    let mut seq2: Vec<u8> = Vec::new();

    while let Some(Ok(line)) = reader.next() {
        if line.starts_with('>') {
            // header line
            // id is token after '>' up to whitespace
            let id = line[1..].split_whitespace().next().unwrap_or("");
            if id == "THREE" {
                in_three = true;
                continue;
            } else if in_three {
                // we just finished THREE sequence
                break;
            }
        } else if in_three {
            // collect bases (2-bit encoded)
            for &b in line.as_bytes() {
                if let Some(v) = base_to_2bit(b) {
                    seq2.push(v);
                }
            }
        }
    }

    // 2) Frequencies for k=1 and k=2
    print_freq(&seq2, 1);
    print_freq(&seq2, 2);

    // 3) Specific pattern counts
    let patterns = [
        "GGT",
        "GGTA",
        "GGTATT",
        "GGTATTTTAATT",
        "GGTATTTTAATTTATAGT",
    ];

    for pat in patterns {
        let k = pat.len();
        let map = count_k(&seq2, k);
        let key = encode_pattern(pat);
        let cnt = map.get(&key).copied().unwrap_or(0);
        println!("{}\t{}", cnt, pat);
    }
}

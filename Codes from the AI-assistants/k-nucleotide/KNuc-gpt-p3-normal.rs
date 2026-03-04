use std::collections::HashMap;
use std::io::{self, Read};

fn main() {
    // 1) Read all stdin
    let mut input = Vec::new();
    io::stdin().read_to_end(&mut input).unwrap();

    // 2) Extract FASTA sequence THREE
    let seq = extract_three(&input);
    if seq.is_empty() {
        return;
    }

    // 3) Map A/C/G/T to 0..3
    let mut map_byte_to_code = [255u8; 256];
    map_byte_to_code[b'A' as usize] = 0;
    map_byte_to_code[b'C' as usize] = 1;
    map_byte_to_code[b'G' as usize] = 2;
    map_byte_to_code[b'T' as usize] = 3;
    map_byte_to_code[b'a' as usize] = 0;
    map_byte_to_code[b'c' as usize] = 1;
    map_byte_to_code[b'g' as usize] = 2;
    map_byte_to_code[b't' as usize] = 3;

    let mut codes: Vec<u8> = Vec::with_capacity(seq.len());
    for &b in &seq {
        let c = map_byte_to_code[b as usize];
        if c != 255 {
            codes.push(c);
        }
        // If you want to be strict, you could handle non-ACGT here.
    }

    // 4) Count k=1 and k=2, print frequencies
    let m1 = count_k_all_frames(&codes, 1);
    print_freq_table(&m1, 1);
    println!();

    let m2 = count_k_all_frames(&codes, 2);
    print_freq_table(&m2, 2);
    println!();

    // 5) Count specific k values and print requested sequences
    let queries = [
        "GGT",
        "GGTA",
        "GGTATT",
        "GGTATTTTAATT",
        "GGTATTTTAATTTATAGT",
    ];

    // Group queries by k (so we don't recount unnecessarily)
    // Needed k: 3,4,6,12,18
    let m3 = count_k_all_frames(&codes, 3);
    let m4 = count_k_all_frames(&codes, 4);
    let m6 = count_k_all_frames(&codes, 6);
    let m12 = count_k_all_frames(&codes, 12);
    let m18 = count_k_all_frames(&codes, 18);

    for q in queries {
        let k = q.len();
        let key = encode_kmer_ascii(q.as_bytes());
        let count = match k {
            3 => *m3.get(&key).unwrap_or(&0),
            4 => *m4.get(&key).unwrap_or(&0),
            6 => *m6.get(&key).unwrap_or(&0),
            12 => *m12.get(&key).unwrap_or(&0),
            18 => *m18.get(&key).unwrap_or(&0),
            _ => 0,
        };
        println!("{}\t{}", count, q);
    }
}

// -------- FASTA parsing --------

fn extract_three(input: &[u8]) -> Vec<u8> {
    let mut in_three = false;
    let mut out = Vec::new();

    for line in input.split(|&b| b == b'\n') {
        if line.starts_with(b">") {
            // header line: >ID optional description
            // ID is the token after '>' up to first whitespace
            let mut id_end = 1;
            while id_end < line.len() && !line[id_end].is_ascii_whitespace() {
                id_end += 1;
            }
            let id = &line[1..id_end];

            if in_three {
                // next record begins -> stop collecting
                break;
            }
            in_three = id == b"THREE";
            continue;
        }

        if in_three {
            // sequence line
            out.extend_from_slice(line);
        }
    }

    out
}

// -------- Counting --------

fn count_k_all_frames(codes: &[u8], k: usize) -> HashMap<u64, u32> {
    let mut map: HashMap<u64, u32> = HashMap::new(); // starts small, grows naturally
    if k == 0 || codes.len() < k {
        return map;
    }
    for frame in 0..k {
        update_frame_counts(codes, k, frame, &mut map);
    }
    map
}

// Required “reading-frame” updater shape:
// updates counts for starts i = frame, frame+k, frame+2k, ...
fn update_frame_counts(codes: &[u8], k: usize, frame: usize, map: &mut HashMap<u64, u32>) {
    let n = codes.len();
    let mut i = frame;
    while i + k <= n {
        let mut key: u64 = 0;
        for &c in &codes[i..i + k] {
            key = (key << 2) | (c as u64);
        }
        *map.entry(key).or_insert(0) += 1;
        i += k;
    }
}

// -------- Output helpers --------

fn print_freq_table(map: &HashMap<u64, u32>, k: usize) {
    let total: u32 = map.values().copied().sum();
    let mut items: Vec<(u64, u32)> = map.iter().map(|(&kmer, &cnt)| (kmer, cnt)).collect();

    items.sort_by(|&(a_key, a_cnt), &(b_key, b_cnt)| {
        // primary: descending count
        match b_cnt.cmp(&a_cnt) {
            std::cmp::Ordering::Equal => {
                // secondary: ascending decoded key
                let a_s = decode_kmer(a_key, k);
                let b_s = decode_kmer(b_key, k);
                a_s.cmp(&b_s)
            }
            other => other,
        }
    });

    for (key, cnt) in items {
        let s = decode_kmer(key, k);
        let pct = (cnt as f64) * 100.0 / (total as f64);
        println!("{} {:.3}", s, pct);
    }
}

fn decode_kmer(mut key: u64, k: usize) -> String {
    let mut out = vec![b'A'; k];
    for idx in (0..k).rev() {
        let bits = (key & 0b11) as u8;
        out[idx] = match bits {
            0 => b'A',
            1 => b'C',
            2 => b'G',
            _ => b'T',
        };
        key >>= 2;
    }
    String::from_utf8(out).unwrap()
}

fn encode_kmer_ascii(s: &[u8]) -> u64 {
    let mut key: u64 = 0;
    for &b in s {
        let c = match b {
            b'A' | b'a' => 0u64,
            b'C' | b'c' => 1u64,
            b'G' | b'g' => 2u64,
            b'T' | b't' => 3u64,
            _ => 0u64, // assuming inputs are A/C/G/T
        };
        key = (key << 2) | c;
    }
    key
}

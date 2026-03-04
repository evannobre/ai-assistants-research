use std::collections::HashMap;
use std::io::{self, Read};

fn is_three_header(line: &[u8]) -> bool {
    // Accept: >THREE, >THREE <desc...>, >THREE\n
    line.starts_with(b">THREE")
        && (line.len() == 6 || line.get(6).map(|c| *c == b' ' || *c == b'\t' || *c == b'\r' || *c == b'\n').unwrap_or(true))
}

fn extract_three_sequence(input: &[u8]) -> Vec<u8> {
    // Parse FASTA; return raw sequence bytes (no newlines), uppercased.
    let mut in_three = false;
    let mut seq = Vec::new();

    // Split by '\n' manually to avoid UTF-8 assumptions.
    let mut start = 0usize;
    while start < input.len() {
        let mut end = start;
        while end < input.len() && input[end] != b'\n' { end += 1; }
        let line = &input[start..end];

        if !line.is_empty() && line[0] == b'>' {
            if in_three {
                // End of THREE sequence at next header
                break;
            }
            if is_three_header(line) {
                in_three = true;
            }
        } else if in_three {
            // Sequence line: strip CR, uppercase, append
            for &b in line {
                if b == b'\r' { continue; }
                // ASCII uppercase trick: clear bit 0x20
                let up = b & !0x20;
                seq.push(up);
            }
        }

        start = if end < input.len() { end + 1 } else { end };
    }

    seq
}

fn dna_to_code(b: u8) -> Option<u8> {
    match b {
        b'A' => Some(0),
        b'C' => Some(1),
        b'G' => Some(2),
        b'T' => Some(3),
        _ => None, // ignore unexpected chars (shouldn't happen in benchmark input)
    }
}

fn pack_kmer(codes: &[u8]) -> u64 {
    let mut key: u64 = 0;
    for &c in codes {
        key = (key << 2) | (c as u64);
    }
    key
}

fn unpack_kmer(mut key: u64, k: usize) -> String {
    let mut out = vec![b'A'; k];
    for i in (0..k).rev() {
        let v = (key & 3) as u8;
        out[i] = match v {
            0 => b'A',
            1 => b'C',
            2 => b'G',
            _ => b'T',
        };
        key >>= 2;
    }
    String::from_utf8(out).unwrap()
}

/// Required function: update hashtable for a particular reading frame.
/// It steps by k within the frame and updates counts in the provided HashMap.
fn update_table_for_frame(codes: &[u8], k: usize, frame: usize, table: &mut HashMap<u64, u32>) {
    if k == 0 || frame >= k || codes.len() < k {
        return;
    }
    let mut i = frame;
    while i + k <= codes.len() {
        let key = pack_kmer(&codes[i..i + k]);
        *table.entry(key).or_insert(0) += 1;
        i += k;
    }
}

fn count_kmers_all_frames(codes: &[u8], k: usize) -> HashMap<u64, u32> {
    // "grow the hashtable from a small default size"
    let mut table: HashMap<u64, u32> = HashMap::new();
    for frame in 0..k {
        update_table_for_frame(codes, k, frame, &mut table);
    }
    table
}

fn print_frequencies(codes: &[u8], k: usize) {
    let table = count_kmers_all_frames(codes, k);
    let total: u64 = table.values().map(|&v| v as u64).sum();

    let mut items: Vec<(String, u32)> = table
        .into_iter()
        .map(|(key, count)| (unpack_kmer(key, k), count))
        .collect();

    // Sort: descending count, then ascending key string
    items.sort_by(|a, b| {
        b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0))
    });

    for (s, c) in items {
        let pct = 100.0 * (c as f64) / (total as f64);
        println!("{} {:.3}", s, pct);
    }
    println!();
}

fn count_specific(codes: &[u8], seq: &str) -> u32 {
    let bytes = seq.as_bytes();
    let mut tmp = Vec::with_capacity(bytes.len());
    for &b in bytes {
        if let Some(c) = dna_to_code(b) {
            tmp.push(c);
        } else {
            return 0;
        }
    }
    let k = tmp.len();
    let table = count_kmers_all_frames(codes, k);
    let key = pack_kmer(&tmp);
    *table.get(&key).unwrap_or(&0)
}

fn main() -> io::Result<()> {
    // Read stdin completely (as required by user request)
    let mut input = Vec::new();
    io::stdin().read_to_end(&mut input)?;

    let three_seq = extract_three_sequence(&input);

    // Map to 0/1/2/3 codes
    let mut codes = Vec::with_capacity(three_seq.len());
    for &b in &three_seq {
        if let Some(c) = dna_to_code(b) {
            codes.push(c);
        }
    }

    // Frequencies
    print_frequencies(&codes, 1);
    print_frequencies(&codes, 2);

    // Specific sequences
    let interests = [
        "GGT",
        "GGTA",
        "GGTATT",
        "GGTATTTTAATT",
        "GGTATTTTAATTTATAGT",
    ];
    for s in interests {
        let c = count_specific(&codes, s);
        println!("{} {}", c, s);
    }

    Ok(())
}

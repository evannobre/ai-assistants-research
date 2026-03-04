use std::cmp::Ordering;
use std::collections::HashMap;
use std::io::{self, BufRead, Write};

fn base_to_bits(b: u8) -> Option<u8> {
    match b {
        b'A' => Some(0),
        b'C' => Some(1),
        b'G' => Some(2),
        b'T' => Some(3),
        _ => None,
    }
}

fn bits_to_base(x: u8) -> u8 {
    match x {
        0 => b'A',
        1 => b'C',
        2 => b'G',
        _ => b'T',
    }
}

fn encode_kmer(s: &[u8]) -> u64 {
    let mut key: u64 = 0;
    for &ch in s {
        let b = match ch {
            b'a'..=b'z' => ch - 32,
            _ => ch,
        };
        let bits = base_to_bits(b).expect("query contains non-ACGT");
        key = (key << 2) | bits as u64;
    }
    key
}

fn decode_kmer(mut key: u64, k: usize) -> Vec<u8> {
    let mut out = vec![0u8; k];
    for i in (0..k).rev() {
        let bits = (key & 3) as u8;
        out[i] = bits_to_base(bits);
        key >>= 2;
    }
    out
}

fn count_kmers(seq_bits: &[u8], k: usize) -> HashMap<u64, u32> {
    let mut map: HashMap<u64, u32> = HashMap::new();
    if k == 0 || seq_bits.len() < k {
        return map;
    }

    let mask: u64 = if 2 * k == 64 {
        u64::MAX
    } else {
        (1u64 << (2 * k)) - 1
    };

    let mut key: u64 = 0;
    for (i, &b) in seq_bits.iter().enumerate() {
        key = ((key << 2) | (b as u64)) & mask;
        if i + 1 >= k {
            *map.entry(key).or_insert(0) += 1;
        }
    }
    map
}

fn print_freq<W: Write>(out: &mut W, seq_bits: &[u8], k: usize) -> io::Result<()> {
    let map = count_kmers(seq_bits, k);

    let total: u32 = map.values().copied().sum();
    let mut items: Vec<(Vec<u8>, u32)> = map
        .into_iter()
        .map(|(key, count)| (decode_kmer(key, k), count))
        .collect();

    items.sort_by(|(a_s, a_c), (b_s, b_c)| {
        match b_c.cmp(a_c) {
            Ordering::Equal => a_s.cmp(b_s),
            other => other,
        }
    });

    for (s, c) in items {
        let pct = (c as f64) * 100.0 / (total as f64);
        writeln!(out, "{} {:.3}", String::from_utf8_lossy(&s), pct)?;
    }
    writeln!(out)?;
    Ok(())
}

fn main() -> io::Result<()> {
    // 1) Read FASTA and capture only the >THREE sequence.
    let stdin = io::stdin();
    let mut capturing = false;
    let mut seq: Vec<u8> = Vec::new();

    for line_res in stdin.lock().lines() {
        let line = line_res?;
        if line.starts_with('>') {
            if capturing {
                // stop at next header after >THREE
                break;
            }
            capturing = line.starts_with(">THREE");
            continue;
        }
        if capturing {
            // append bases only (normalize to uppercase)
            for &ch in line.as_bytes() {
                let up = if (b'a'..=b'z').contains(&ch) { ch - 32 } else { ch };
                if matches!(up, b'A' | b'C' | b'G' | b'T') {
                    seq.push(up);
                }
            }
        }
    }

    // 2) Convert to 2-bit codes for rolling.
    let mut seq_bits: Vec<u8> = Vec::with_capacity(seq.len());
    for &b in &seq {
        // safe since we filtered to A/C/G/T
        seq_bits.push(base_to_bits(b).unwrap());
    }

    let mut out = io::BufWriter::new(io::stdout().lock());

    // 3) Frequency tables
    print_freq(&mut out, &seq_bits, 1)?;
    print_freq(&mut out, &seq_bits, 2)?;

    // 4) Specific oligos
    let queries = [
        b"GGT".as_slice(),
        b"GGTA".as_slice(),
        b"GGTATT".as_slice(),
        b"GGTATTTTAATT".as_slice(),
        b"GGTATTTTAATTTATAGT".as_slice(),
    ];

    for &q in &queries {
        let k = q.len();
        let map = count_kmers(&seq_bits, k);
        let key = encode_kmer(q);
        let count = map.get(&key).copied().unwrap_or(0);
        writeln!(out, "{}\t{}", count, String::from_utf8_lossy(q))?;
    }

    Ok(())
}

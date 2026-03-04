use std::env;
use std::io::{self, Write};

const LINE_LEN: usize = 60;

// Naïve LCG parameters (must match spec)
const IM: u32 = 139_968;
const IA: u32 = 3_877;
const IC: u32 = 29_573;

#[derive(Clone, Copy)]
struct Entry {
    ch: u8,      // nucleotide as byte
    prob: f64,   // expected probability
}

fn make_cumulative(table: &[Entry]) -> Vec<(u8, f64)> {
    let mut cum = 0.0_f64;
    let mut out = Vec::with_capacity(table.len());
    for e in table {
        cum += e.prob;
        out.push((e.ch, cum));
    }
    out
}

// Random(Max): seed = (seed*IA + IC) % IM ; return seed/IM
fn next_rand(seed: &mut u32) -> f64 {
    *seed = (*seed * IA + IC) % IM;
    (*seed as f64) / (IM as f64)
}

// Linear search against cumulative probabilities
fn pick_char(seed: &mut u32, cum: &[(u8, f64)]) -> u8 {
    let r = next_rand(seed);
    for &(ch, cp) in cum {
        if r < cp {
            return ch;
        }
    }
    // In case of rounding (should be rare), fall back to last element.
    cum[cum.len() - 1].0
}

fn write_wrapped<W: Write, F: FnMut() -> u8>(
    out: &mut W,
    total: usize,
    mut gen: F,
) -> io::Result<()> {
    let mut line_buf = [0u8; LINE_LEN];

    let mut produced = 0usize;
    while produced < total {
        let chunk = std::cmp::min(LINE_LEN, total - produced);
        for i in 0..chunk {
            line_buf[i] = gen();
        }
        out.write_all(&line_buf[..chunk])?;
        out.write_all(b"\n")?;
        produced += chunk;
    }
    Ok(())
}

fn main() -> io::Result<()> {
    let n: usize = env::args()
        .nth(1)
        .and_then(|s| s.parse::<usize>().ok())
        .unwrap_or(1000);

    let stdout = io::stdout();
    let mut out = io::BufWriter::new(stdout.lock());

    // Fixed ALU sequence (standard Benchmarks Game content)
    const ALU: &str =
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAATACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA";

    // Alphabet #1: IUB ambiguity codes (standard)
    let iub = [
        Entry { ch: b'a', prob: 0.27 },
        Entry { ch: b'c', prob: 0.12 },
        Entry { ch: b'g', prob: 0.12 },
        Entry { ch: b't', prob: 0.27 },
        Entry { ch: b'B', prob: 0.02 },
        Entry { ch: b'D', prob: 0.02 },
        Entry { ch: b'H', prob: 0.02 },
        Entry { ch: b'K', prob: 0.02 },
        Entry { ch: b'M', prob: 0.02 },
        Entry { ch: b'N', prob: 0.02 },
        Entry { ch: b'R', prob: 0.02 },
        Entry { ch: b'S', prob: 0.02 },
        Entry { ch: b'V', prob: 0.02 },
        Entry { ch: b'W', prob: 0.02 },
        Entry { ch: b'Y', prob: 0.02 },
    ];

    // Alphabet #2: Homo sapiens frequencies (standard)
    let homosapiens = [
        Entry { ch: b'a', prob: 0.3029549426680 },
        Entry { ch: b'c', prob: 0.1979883004921 },
        Entry { ch: b'g', prob: 0.1975473066391 },
        Entry { ch: b't', prob: 0.3015094502008 },
    ];

    // Convert to cumulative probabilities (no scaling tricks)
    let iub_cum = make_cumulative(&iub);
    let hs_cum = make_cumulative(&homosapiens);

    // Naïve LCG seed
    let mut seed: u32 = 42;

    // 1) Repeated ALU sequence: 2*n
    out.write_all(b">ONE Homo sapiens alu\n")?;
    let alu_bytes = ALU.as_bytes();
    let mut idx = 0usize;
    write_wrapped(&mut out, 2 * n, || {
        let ch = alu_bytes[idx % alu_bytes.len()];
        idx += 1;
        ch
    })?;

    // 2) Random IUB: n
    out.write_all(b">TWO IUB ambiguity codes\n")?;
    write_wrapped(&mut out, n, || pick_char(&mut seed, &iub_cum))?;

    // 3) Random Homo sapiens: n
    out.write_all(b">THREE Homo sapiens frequency\n")?;
    write_wrapped(&mut out, n, || pick_char(&mut seed, &hs_cum))?;

    out.flush()?;
    Ok(())
}

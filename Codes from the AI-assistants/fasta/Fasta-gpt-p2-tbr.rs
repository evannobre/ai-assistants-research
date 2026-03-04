use std::env;
use std::io::{self, Write};

const LINE_LEN: usize = 60;

// Naïve LCG constants (Benchmarks Game fasta)
const IM: u32 = 139_968;
const IA: u32 = 3_877;
const IC: u32 = 29_573;

struct Lcg {
    seed: u32,
}

impl Lcg {
    #[inline]
    fn next_f64(&mut self) -> f64 {
        // seed = (seed * IA + IC) % IM
        self.seed = (self.seed.wrapping_mul(IA).wrapping_add(IC)) % IM;
        (self.seed as f64) / (IM as f64) // in [0, 1)
    }
}

#[derive(Clone, Copy)]
struct Weight {
    ch: u8,
    p: f64,
}

fn build_cumulative(weights: &[Weight]) -> Vec<(u8, f64)> {
    let mut out = Vec::with_capacity(weights.len());
    let mut acc = 0.0f64;
    for w in weights {
        acc += w.p;
        out.push((w.ch, acc));
    }
    // acc should be ~1.0; minor FP drift is OK for this benchmark
    out
}

#[inline]
fn pick_weighted(r: f64, cum: &[(u8, f64)]) -> u8 {
    // Small arrays; linear scan is fast and branch-predictable.
    for &(ch, c) in cum {
        if r < c {
            return ch;
        }
    }
    // In case of FP rounding, fall back to last.
    cum[cum.len() - 1].0
}

fn write_header(buf: &mut Vec<u8>, title: &str) {
    buf.extend_from_slice(b">");
    buf.extend_from_slice(title.as_bytes());
    buf.push(b'\n');
}

fn flush_if_needed<W: Write>(w: &mut W, buf: &mut Vec<u8>, threshold: usize) -> io::Result<()> {
    if buf.len() >= threshold {
        w.write_all(buf)?;
        buf.clear();
    }
    Ok(())
}

fn write_repeat<W: Write>(
    w: &mut W,
    out: &mut Vec<u8>,
    s: &[u8],
    mut total_len: usize,
) -> io::Result<()> {
    let mut pos = 0usize;
    let threshold = 64 * 1024;

    while total_len > 0 {
        let line = total_len.min(LINE_LEN);

        // Write 'line' bytes from s, wrapping around.
        let mut remaining = line;
        while remaining > 0 {
            let chunk = (s.len() - pos).min(remaining);
            out.extend_from_slice(&s[pos..pos + chunk]);
            pos += chunk;
            if pos == s.len() {
                pos = 0;
            }
            remaining -= chunk;

            flush_if_needed(w, out, threshold)?;
        }

        out.push(b'\n');
        total_len -= line;

        flush_if_needed(w, out, threshold)?;
    }

    Ok(())
}

fn write_random<W: Write>(
    w: &mut W,
    out: &mut Vec<u8>,
    rng: &mut Lcg,
    cum: &[(u8, f64)],
    mut total_len: usize,
) -> io::Result<()> {
    let threshold = 64 * 1024;

    while total_len > 0 {
        let line = total_len.min(LINE_LEN);

        for _ in 0..line {
            let r = rng.next_f64();
            out.push(pick_weighted(r, cum));
        }
        out.push(b'\n');

        total_len -= line;
        flush_if_needed(w, out, threshold)?;
    }

    Ok(())
}

fn main() -> io::Result<()> {
    let n: usize = env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(0);

    // Fixed alu fragment (Benchmarks Game fasta)
    const ALU: &str =
        "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG\
         GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAG\
         ACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAA\
         ATACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATC\
         CCAGCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACC\
         CGGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGC\
         ACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA";

    // IUB ambiguity codes
    let iub = build_cumulative(&[
        Weight { ch: b'a', p: 0.27 },
        Weight { ch: b'c', p: 0.12 },
        Weight { ch: b'g', p: 0.12 },
        Weight { ch: b't', p: 0.27 },
        Weight { ch: b'B', p: 0.02 },
        Weight { ch: b'D', p: 0.02 },
        Weight { ch: b'H', p: 0.02 },
        Weight { ch: b'K', p: 0.02 },
        Weight { ch: b'M', p: 0.02 },
        Weight { ch: b'N', p: 0.02 },
        Weight { ch: b'R', p: 0.02 },
        Weight { ch: b'S', p: 0.02 },
        Weight { ch: b'V', p: 0.02 },
        Weight { ch: b'W', p: 0.02 },
        Weight { ch: b'Y', p: 0.02 },
    ]);

    // Homo sapiens frequency
    let homosapiens = build_cumulative(&[
        Weight { ch: b'a', p: 0.3029549426680 },
        Weight { ch: b'c', p: 0.1979883004921 },
        Weight { ch: b'g', p: 0.1975473066391 },
        Weight { ch: b't', p: 0.3015094502008 },
    ]);

    let mut rng = Lcg { seed: 42 };

    let stdout = io::stdout();
    let mut w = io::BufWriter::new(stdout.lock());
    let mut buf: Vec<u8> = Vec::with_capacity(64 * 1024);

    // 1) Repeat alu (2*n)
    write_header(&mut buf, "ONE Homo sapiens alu");
    w.write_all(&buf)?;
    buf.clear();
    write_repeat(&mut w, &mut buf, ALU.as_bytes(), 2 * n)?;

    // 2) Random IUB (3*n)
    write_header(&mut buf, "TWO IUB ambiguity codes");
    w.write_all(&buf)?;
    buf.clear();
    write_random(&mut w, &mut buf, &mut rng, &iub, 3 * n)?;

    // 3) Random Homo sapiens (5*n)
    write_header(&mut buf, "THREE Homo sapiens frequency");
    w.write_all(&buf)?;
    buf.clear();
    write_random(&mut w, &mut buf, &mut rng, &homosapiens, 5 * n)?;

    // Flush remaining buffered bytes
    if !buf.is_empty() {
        w.write_all(&buf)?;
    }
    w.flush()?;
    Ok(())
}

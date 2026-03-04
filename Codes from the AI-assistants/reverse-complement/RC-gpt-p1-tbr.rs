use std::env;
use std::fs::File;
use std::io::{self, BufRead, BufReader, BufWriter, Write};

const OUT_WIDTH: usize = 60;

fn build_complement_table() -> [u8; 256] {
    let mut t = [0u8; 256];
    for i in 0..256 {
        t[i] = i as u8; // default: identity
    }

    // IUPAC complements (DNA)
    // A <-> T, C <-> G
    // M <-> K, R <-> Y, S <-> S, W <-> W
    // B <-> V, D <-> H, N <-> N
    // Also include lowercase.
    let pairs = [
        (b'A', b'T'), (b'C', b'G'), (b'G', b'C'), (b'T', b'A'),
        (b'M', b'K'), (b'K', b'M'),
        (b'R', b'Y'), (b'Y', b'R'),
        (b'S', b'S'), (b'W', b'W'),
        (b'B', b'V'), (b'V', b'B'),
        (b'D', b'H'), (b'H', b'D'),
        (b'N', b'N'),
        // Some FASTA inputs may contain U (RNA); treat as A-complement like T <-> A rule doesn’t fit.
        // Common convention: U complements A.
        (b'U', b'A'),
    ];

    for (a, b) in pairs {
        t[a as usize] = b;
    }

    // Lowercase variants
    for i in 0..256 {
        let c = i as u8;
        if c.is_ascii_uppercase() {
            let lc = c.to_ascii_lowercase();
            let comp_uc = t[i];
            t[lc as usize] = comp_uc.to_ascii_lowercase();
        }
    }

    // Ensure lowercase u too
    t[b'u' as usize] = b'a';

    t
}

fn flush_reverse_complement<W: Write>(
    seq: &[u8],
    comp: &[u8; 256],
    out: &mut W,
) -> io::Result<()> {
    let mut col = 0usize;

    for &b in seq.iter().rev() {
        let cb = comp[b as usize];
        out.write_all(&[cb])?;
        col += 1;
        if col == OUT_WIDTH {
            out.write_all(b"\n")?;
            col = 0;
        }
    }
    if col != 0 {
        out.write_all(b"\n")?;
    }
    Ok(())
}

fn main() -> io::Result<()> {
    let path = env::args().nth(1).unwrap_or_else(|| {
        eprintln!("Usage: reverse_complement <input_fasta_file>");
        std::process::exit(2);
    });

    let comp = build_complement_table();

    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let stdout = io::stdout();
    let mut out = BufWriter::new(stdout.lock());

    let mut seq_buf: Vec<u8> = Vec::new();
    let mut have_record = false;

    for line_res in reader.lines() {
        let line = line_res?;
        let bytes = line.as_bytes();

        if bytes.first() == Some(&b'>') {
            // New header -> flush previous sequence if present
            if have_record {
                flush_reverse_complement(&seq_buf, &comp, &mut out)?;
                seq_buf.clear();
            } else {
                have_record = true;
            }

            out.write_all(line.as_bytes())?;
            out.write_all(b"\n")?;
        } else {
            // Append non-whitespace nucleotide bytes
            // (Handles typical FASTA lines; tolerates spaces/tabs just in case.)
            seq_buf.extend(bytes.iter().copied().filter(|b| !b.is_ascii_whitespace()));
        }
    }

    // Flush last record
    if have_record {
        flush_reverse_complement(&seq_buf, &comp, &mut out)?;
    }

    out.flush()?;
    Ok(())
}

use std::env;
use std::fs::File;
use std::io::{self, BufRead, BufReader, BufWriter, Read, Write};

const LINE_WRAP: usize = 60;

/// Build an ASCII lookup table mapping byte -> complement byte.
/// Unmapped bytes map to themselves (safe default).
fn build_complement_table() -> [u8; 256] {
    let mut t = [0u8; 256];
    for i in 0..256 {
        t[i] = i as u8;
    }

    // Uppercase IUPAC DNA complements
    t[b'A' as usize] = b'T';
    t[b'C' as usize] = b'G';
    t[b'G' as usize] = b'C';
    t[b'T' as usize] = b'A';
    t[b'U' as usize] = b'A';

    t[b'M' as usize] = b'K';
    t[b'R' as usize] = b'Y';
    t[b'W' as usize] = b'W';
    t[b'S' as usize] = b'S';
    t[b'Y' as usize] = b'R';
    t[b'K' as usize] = b'M';

    t[b'V' as usize] = b'B';
    t[b'H' as usize] = b'D';
    t[b'D' as usize] = b'H';
    t[b'B' as usize] = b'V';
    t[b'N' as usize] = b'N';

    // Lowercase equivalents
    t[b'a' as usize] = b't';
    t[b'c' as usize] = b'g';
    t[b'g' as usize] = b'c';
    t[b't' as usize] = b'a';
    t[b'u' as usize] = b'a';

    t[b'm' as usize] = b'k';
    t[b'r' as usize] = b'y';
    t[b'w' as usize] = b'w';
    t[b's' as usize] = b's';
    t[b'y' as usize] = b'r';
    t[b'k' as usize] = b'm';

    t[b'v' as usize] = b'b';
    t[b'h' as usize] = b'd';
    t[b'd' as usize] = b'h';
    t[b'b' as usize] = b'v';
    t[b'n' as usize] = b'n';

    t
}

/// Write reverse-complement of `seq` to `out`, wrapped at 60 chars/line.
fn write_reverse_complement<W: Write>(
    out: &mut W,
    seq: &[u8],
    comp: &[u8; 256],
) -> io::Result<()> {
    // Small reusable line buffer: 60 bases + '\n'
    let mut line = Vec::with_capacity(LINE_WRAP + 1);

    for &b in seq.iter().rev() {
        line.push(comp[b as usize]);
        if line.len() == LINE_WRAP {
            out.write_all(&line)?;
            out.write_all(b"\n")?;
            line.clear();
        }
    }

    if !line.is_empty() {
        out.write_all(&line)?;
        out.write_all(b"\n")?;
    }

    Ok(())
}

fn open_input(path: &str) -> io::Result<Box<dyn Read>> {
    if path == "-" {
        Ok(Box::new(io::stdin().lock()))
    } else {
        Ok(Box::new(File::open(path)?))
    }
}

fn main() -> io::Result<()> {
    let mut args = env::args().skip(1);
    let path = args.next().unwrap_or_else(|| "-".to_string());

    let comp = build_complement_table();

    let input = open_input(&path)?;
    let reader = BufReader::new(input);
    let stdout = io::stdout();
    let mut out = BufWriter::new(stdout.lock());

    // Buffer to accumulate the current record's sequence (no newlines).
    let mut seq: Vec<u8> = Vec::new();

    for line_res in reader.lines() {
        let line = line_res?;
        if line.as_bytes().first() == Some(&b'>') {
            // New header: flush previous record sequence (if any)
            if !seq.is_empty() {
                write_reverse_complement(&mut out, &seq, &comp)?;
                seq.clear();
            }
            // Print header as-is (restore newline)
            out.write_all(line.as_bytes())?;
            out.write_all(b"\n")?;
        } else {
            // Append sequence characters; FASTA lines have no spaces in benchmark inputs,
            // but we conservatively strip trailing whitespace.
            let trimmed = line.trim_end();
            seq.extend_from_slice(trimmed.as_bytes());
        }
    }

    // Flush last record
    if !seq.is_empty() {
        write_reverse_complement(&mut out, &seq, &comp)?;
    }

    out.flush()?;
    Ok(())
}

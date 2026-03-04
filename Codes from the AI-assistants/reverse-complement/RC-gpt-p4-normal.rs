use std::io::{self, BufRead, BufReader, BufWriter, Write};

const LINE_LEN: usize = 60;

fn build_complement_table() -> [u8; 256] {
    let mut t = [b'N'; 256];

    // Identity defaults for whitespace/newlines (we won't store them in seq, but safe anyway)
    t[b'\n' as usize] = b'\n';
    t[b'\r' as usize] = b'\r';

    // Helper to set both uppercase and lowercase mappings
    let mut set = |a: u8, b: u8| {
        t[a as usize] = b;
        t[(a as char).to_ascii_lowercase() as usize] = (b as char).to_ascii_lowercase() as u8;
    };

    // Given complement rules
    set(b'A', b'T');
    set(b'C', b'G');
    set(b'G', b'C');
    set(b'T', b'A');
    set(b'U', b'A'); // T/U meaning T; complement A

    set(b'M', b'K');
    set(b'R', b'Y');
    set(b'W', b'W');
    set(b'S', b'S');
    set(b'Y', b'R');
    set(b'K', b'M');

    set(b'V', b'B');
    set(b'H', b'D');
    set(b'D', b'H');
    set(b'B', b'V');

    set(b'N', b'N');

    t
}

fn write_revcomp<W: Write>(out: &mut W, header: &[u8], seq: &[u8], comp: &[u8; 256]) -> io::Result<()> {
    out.write_all(header)?;
    if !header.ends_with(b"\n") {
        out.write_all(b"\n")?;
    }

    // Write reverse-complement in 60-char FASTA lines.
    // We traverse backwards, but emit forward within each output line.
    let mut i = seq.len();
    while i > 0 {
        let start = i.saturating_sub(LINE_LEN);
        // slice = seq[start..i], but we need reverse order and complemented
        for &ch in seq[start..i].iter().rev() {
            out.write_all(&[comp[ch as usize]])?;
        }
        out.write_all(b"\n")?;
        i = start;
    }
    Ok(())
}

fn main() -> io::Result<()> {
    let stdin = io::stdin();
    let mut reader = BufReader::new(stdin.lock());

    let stdout = io::stdout();
    let mut out = BufWriter::new(stdout.lock());

    let comp = build_complement_table();

    let mut line = Vec::<u8>::new();
    let mut header = Vec::<u8>::new();
    let mut seq = Vec::<u8>::new();

    loop {
        line.clear();
        let n = reader.read_until(b'\n', &mut line)?;
        if n == 0 {
            break; // EOF
        }

        if line.starts_with(b">") {
            if !header.is_empty() {
                write_revcomp(&mut out, &header, &seq, &comp)?;
            }
            header.clear();
            header.extend_from_slice(&line);
            seq.clear();
        } else {
            // Strip trailing newline and optional CR, then append
            while let Some(&last) = line.last() {
                if last == b'\n' || last == b'\r' {
                    line.pop();
                } else {
                    break;
                }
            }
            seq.extend_from_slice(&line);
        }
    }

    if !header.is_empty() {
        write_revcomp(&mut out, &header, &seq, &comp)?;
    }

    out.flush()?;
    Ok(())
}

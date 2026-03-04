use std::io::{self, Read, Write, BufRead, BufReader, BufWriter};

const OUT_LINE_LEN: usize = 60;

fn build_complement_table() -> [u8; 256] {
    let mut c = [0u8; 256];

    // Default: identity (so unexpected chars pass through unchanged)
    for i in 0..256 {
        c[i] = i as u8;
    }

    // Helper to set both upper/lower mappings
    let mut set_pair = |a: u8, b: u8| {
        c[a as usize] = b;
        c[(a.to_ascii_lowercase()) as usize] = b.to_ascii_lowercase();
    };

    // IUPAC complements
    set_pair(b'A', b'T');
    set_pair(b'C', b'G');
    set_pair(b'G', b'C');
    set_pair(b'T', b'A');
    set_pair(b'U', b'A');

    set_pair(b'M', b'K');
    set_pair(b'R', b'Y');
    set_pair(b'W', b'W');
    set_pair(b'S', b'S');
    set_pair(b'Y', b'R');
    set_pair(b'K', b'M');

    set_pair(b'V', b'B');
    set_pair(b'H', b'D');
    set_pair(b'D', b'H');
    set_pair(b'B', b'V');

    set_pair(b'N', b'N');

    c
}

fn write_revcomp<W: Write>(out: &mut W, seq: &[u8], comp: &[u8; 256]) -> io::Result<()> {
    // Write reverse-complement with 60-char lines
    let mut col = 0usize;

    for &b in seq.iter().rev() {
        let cb = comp[b as usize];
        out.write_all(&[cb])?;
        col += 1;
        if col == OUT_LINE_LEN {
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
    let stdin = io::stdin();
    let mut reader = BufReader::with_capacity(1 << 20, stdin.lock()); // 1 MiB buffer

    let stdout = io::stdout();
    let mut out = BufWriter::with_capacity(1 << 20, stdout.lock()); // 1 MiB buffer

    let comp = build_complement_table();

    let mut line = Vec::<u8>::with_capacity(256);
    let mut header: Option<Vec<u8>> = None;
    let mut seq: Vec<u8> = Vec::with_capacity(1024);

    loop {
        line.clear();
        let n = reader.read_until(b'\n', &mut line)?;
        if n == 0 {
            // EOF: flush last record if present
            if let Some(h) = header.take() {
                out.write_all(&h)?;
                if !h.ends_with(b"\n") {
                    out.write_all(b"\n")?;
                }
                write_revcomp(&mut out, &seq, &comp)?;
            }
            break;
        }

        // Trim trailing '\n' and optional '\r'
        while line.last().is_some_and(|&x| x == b'\n' || x == b'\r') {
            line.pop();
        }

        if line.first() == Some(&b'>') {
            // New header starts → flush previous record first
            if let Some(h) = header.replace({
                let mut h = line.clone();
                h.push(b'\n');
                h
            }) {
                out.write_all(&h)?;
                if !h.ends_with(b"\n") {
                    out.write_all(b"\n")?;
                }
                write_revcomp(&mut out, &seq, &comp)?;
                seq.clear();
            }
        } else {
            // Sequence line: append bases (already trimmed)
            seq.extend_from_slice(&line);
        }
    }

    out.flush()?;
    Ok(())
}

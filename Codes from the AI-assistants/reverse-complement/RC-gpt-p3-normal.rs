use std::io::{self, Read, BufRead, BufReader, Write, BufWriter};

const LINE_WIDTH: usize = 60;

fn build_complement_table() -> [u8; 256] {
    // Default: identity (so unknown bytes pass through unchanged)
    let mut t = [0u8; 256];
    for i in 0..256 {
        t[i] = i as u8;
    }

    // Helper to set both uppercase and lowercase mappings.
    let mut set = |a: u8, b: u8| {
        t[a as usize] = b;
        // lowercase variants if ASCII letter:
        if a.is_ascii_alphabetic() && b.is_ascii_alphabetic() {
            t[(a.to_ascii_lowercase()) as usize] = b.to_ascii_lowercase();
        }
    };

    // IUPAC complements (as requested)
    set(b'A', b'T');
    set(b'C', b'G');
    set(b'G', b'C');
    set(b'T', b'A');
    set(b'U', b'A');

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

fn write_reverse_complement<W: Write>(
    out: &mut W,
    header: &[u8],
    seq: &[u8],
    comp: &[u8; 256],
) -> io::Result<()> {
    // Header as-is
    out.write_all(header)?;
    if !header.ends_with(b"\n") {
        out.write_all(b"\n")?;
    }

    // Stream reverse-complement in LINE_WIDTH chunks
    let mut line_buf = [0u8; LINE_WIDTH];
    let mut used = 0usize;

    for &base in seq.iter().rev() {
        line_buf[used] = comp[base as usize];
        used += 1;
        if used == LINE_WIDTH {
            out.write_all(&line_buf)?;
            out.write_all(b"\n")?;
            used = 0;
        }
    }

    if used != 0 {
        out.write_all(&line_buf[..used])?;
        out.write_all(b"\n")?;
    }

    Ok(())
}

fn main() -> io::Result<()> {
    let stdin = io::stdin();
    let mut reader = BufReader::new(stdin.lock());

    let stdout = io::stdout();
    let mut out = BufWriter::new(stdout.lock());

    let comp = build_complement_table();

    let mut current_header: Option<Vec<u8>> = None;
    let mut seq: Vec<u8> = Vec::new();

    let mut line = Vec::<u8>::new();
    loop {
        line.clear();
        let n = reader.read_until(b'\n', &mut line)?;
        if n == 0 {
            break; // EOF
        }

        if line.first() == Some(&b'>') {
            // Flush previous record if any
            if let Some(h) = current_header.as_ref() {
                write_reverse_complement(&mut out, h, &seq, &comp)?;
            }
            current_header = Some(line.clone());
            seq.clear();
        } else {
            // Append sequence bytes (strip \n and optional \r)
            // This grows seq incrementally (no single huge allocation based on file size).
            if line.ends_with(b"\n") {
                line.pop();
                if line.ends_with(b"\r") {
                    line.pop();
                }
            }
            seq.extend_from_slice(&line);
        }
    }

    // Flush last record
    if let Some(h) = current_header.as_ref() {
        write_reverse_complement(&mut out, h, &seq, &comp)?;
    }

    out.flush()?;
    Ok(())
}

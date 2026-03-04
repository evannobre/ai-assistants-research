use std::env;
use std::fs::File;
use std::io::{self, BufRead, BufReader, BufWriter, Read, Write};

const LINE_WIDTH: usize = 60;

fn build_complement_table() -> [u8; 256] {
    // Default: identity (unchanged). Then override known bases.
    let mut t = [0u8; 256];
    for i in 0..256 {
        t[i] = i as u8;
    }

    // IUPAC DNA complements (uppercase)
    // A<->T, C<->G, M<->K, R<->Y, S<->S, W<->W, B<->V, D<->H, N<->N
    let pairs = [
        (b'A', b'T'),
        (b'C', b'G'),
        (b'M', b'K'),
        (b'R', b'Y'),
        (b'S', b'S'),
        (b'W', b'W'),
        (b'B', b'V'),
        (b'D', b'H'),
        (b'H', b'D'),
        (b'V', b'B'),
        (b'N', b'N'),
    ];

    for (a, b) in pairs {
        t[a as usize] = b;
        t[b as usize] = a;
    }

    // Lowercase equivalents
    let pairs_lc = [
        (b'a', b't'),
        (b'c', b'g'),
        (b'm', b'k'),
        (b'r', b'y'),
        (b's', b's'),
        (b'w', b'w'),
        (b'b', b'v'),
        (b'd', b'h'),
        (b'h', b'd'),
        (b'v', b'b'),
        (b'n', b'n'),
    ];
    for (a, b) in pairs_lc {
        t[a as usize] = b;
        t[b as usize] = a;
    }

    // Sometimes FASTA may contain U (RNA) – treat U like T for complementing purposes.
    // If you want strict DNA only, you can remove these lines.
    t[b'U' as usize] = b'A';
    t[b'u' as usize] = b'a';

    t
}

fn flush_record<W: Write>(
    seq: &mut Vec<u8>,
    comp: &[u8; 256],
    out: &mut W,
) -> io::Result<()> {
    // Write reverse-complement wrapped at LINE_WIDTH, without allocating a reversed copy.
    let mut col = 0usize;

    for &ch in seq.iter().rev() {
        let c = comp[ch as usize];
        out.write_all(&[c])?;
        col += 1;
        if col == LINE_WIDTH {
            out.write_all(b"\n")?;
            col = 0;
        }
    }

    if col != 0 {
        out.write_all(b"\n")?;
    }

    seq.clear();
    Ok(())
}

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();

    // Input: file path in args[1], else stdin.
    let reader: Box<dyn BufRead> = if args.len() >= 2 {
        let f = File::open(&args[1])?;
        Box::new(BufReader::new(f))
    } else {
        // BufReader on stdin
        let stdin = io::stdin();
        Box::new(BufReader::new(stdin.lock()))
    };

    let stdout = io::stdout();
    let mut out = BufWriter::new(stdout.lock());

    let comp = build_complement_table();
    let mut seq: Vec<u8> = Vec::with_capacity(1024 * 1024);

    for line_res in reader.lines() {
        let line = line_res?;
        if line.starts_with('>') {
            // flush previous record before printing new header
            if !seq.is_empty() {
                flush_record(&mut seq, &comp, &mut out)?;
            }
            out.write_all(line.as_bytes())?;
            out.write_all(b"\n")?;
        } else {
            // Append sequence data (strip whitespace/newlines; line from .lines() has no '\n')
            // FASTA typically has only ACGT...; we keep bytes as-is.
            seq.extend_from_slice(line.trim_end().as_bytes());
        }
    }

    // flush last record
    if !seq.is_empty() {
        flush_record(&mut seq, &comp, &mut out)?;
    }

    out.flush()?;
    Ok(())
}

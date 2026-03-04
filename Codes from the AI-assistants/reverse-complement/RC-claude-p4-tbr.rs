use std::io::{self, BufRead, BufReader, BufWriter, Write};

const COMPLEMENT_TABLE: [u8; 256] = {
    let mut table = [0u8; 256];
    table[b'A' as usize] = b'T';
    table[b'C' as usize] = b'G';
    table[b'G' as usize] = b'C';
    table[b'T' as usize] = b'A';
    table[b'U' as usize] = b'A';
    table[b'M' as usize] = b'K';
    table[b'R' as usize] = b'Y';
    table[b'W' as usize] = b'W';
    table[b'S' as usize] = b'S';
    table[b'Y' as usize] = b'R';
    table[b'K' as usize] = b'M';
    table[b'V' as usize] = b'B';
    table[b'H' as usize] = b'D';
    table[b'D' as usize] = b'H';
    table[b'B' as usize] = b'V';
    table[b'N' as usize] = b'N';
    
    // Lowercase variants
    table[b'a' as usize] = b't';
    table[b'c' as usize] = b'g';
    table[b'g' as usize] = b'c';
    table[b't' as usize] = b'a';
    table[b'u' as usize] = b'a';
    table[b'm' as usize] = b'k';
    table[b'r' as usize] = b'y';
    table[b'w' as usize] = b'w';
    table[b's' as usize] = b's';
    table[b'y' as usize] = b'r';
    table[b'k' as usize] = b'm';
    table[b'v' as usize] = b'b';
    table[b'h' as usize] = b'd';
    table[b'd' as usize] = b'h';
    table[b'b' as usize] = b'v';
    table[b'n' as usize] = b'n';
    
    table
};

const LINE_WIDTH: usize = 60;

fn reverse_complement(sequence: &[u8]) -> Vec<u8> {
    sequence.iter()
        .rev()
        .map(|&base| COMPLEMENT_TABLE[base as usize])
        .collect()
}

fn write_fasta_sequence<W: Write>(writer: &mut W, sequence: &[u8]) -> io::Result<()> {
    for chunk in sequence.chunks(LINE_WIDTH) {
        writer.write_all(chunk)?;
        writer.write_all(b"\n")?;
    }
    Ok(())
}

fn main() -> io::Result<()> {
    let stdin = io::stdin();
    let reader = BufReader::with_capacity(64 * 1024, stdin.lock());
    let stdout = io::stdout();
    let mut writer = BufWriter::with_capacity(64 * 1024, stdout.lock());
    
    let mut header = String::new();
    let mut sequence = Vec::with_capacity(1024 * 1024); // Start with 1MB capacity
    
    for line in reader.lines() {
        let line = line?;
        
        if line.starts_with('>') {
            // Process previous sequence if exists
            if !header.is_empty() {
                let rev_comp = reverse_complement(&sequence);
                writer.write_all(header.as_bytes())?;
                writer.write_all(b"\n")?;
                write_fasta_sequence(&mut writer, &rev_comp)?;
                sequence.clear();
            }
            
            // Store new header
            header = line;
        } else {
            // Accumulate sequence data (grow incrementally)
            sequence.extend_from_slice(line.as_bytes());
        }
    }
    
    // Process last sequence
    if !header.is_empty() {
        let rev_comp = reverse_complement(&sequence);
        writer.write_all(header.as_bytes())?;
        writer.write_all(b"\n")?;
        write_fasta_sequence(&mut writer, &rev_comp)?;
    }
    
    writer.flush()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_complement() {
        assert_eq!(reverse_complement(b"ACGT"), b"ACGT");
        assert_eq!(reverse_complement(b"AAAACCCGGT"), b"ACCGGGTTTT");
    }

    #[test]
    fn test_ambiguous_codes() {
        assert_eq!(reverse_complement(b"MRWSYKVHDB"), b"VDHBMRYWSK");
        assert_eq!(reverse_complement(b"N"), b"N");
    }
}
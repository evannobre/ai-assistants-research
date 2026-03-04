use std::io::{self, BufRead, BufReader, BufWriter, Write};

const COMPLEMENT_TABLE: [u8; 256] = create_complement_table();

const fn create_complement_table() -> [u8; 256] {
    let mut table = [0u8; 256];
    let mut i = 0;
    while i < 256 {
        table[i] = i as u8;
        i += 1;
    }
    
    // Uppercase complements
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
    
    // Lowercase complements
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
}

fn reverse_complement(sequence: &[u8]) -> Vec<u8> {
    sequence
        .iter()
        .rev()
        .map(|&base| COMPLEMENT_TABLE[base as usize])
        .collect()
}

fn write_fasta_sequence<W: Write>(
    writer: &mut W,
    sequence: &[u8],
    line_width: usize,
) -> io::Result<()> {
    for chunk in sequence.chunks(line_width) {
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
    
    let mut current_header = Vec::new();
    let mut current_sequence = Vec::new();
    let mut in_sequence = false;
    
    for line in reader.lines() {
        let line = line?;
        
        if line.starts_with('>') {
            // Process previous sequence if exists
            if in_sequence && !current_sequence.is_empty() {
                writer.write_all(&current_header)?;
                writer.write_all(b"\n")?;
                
                let rev_comp = reverse_complement(&current_sequence);
                write_fasta_sequence(&mut writer, &rev_comp, 60)?;
                
                current_sequence.clear();
            }
            
            // Store new header
            current_header.clear();
            current_header.extend_from_slice(line.as_bytes());
            in_sequence = true;
        } else if in_sequence {
            // Accumulate sequence data (skip empty lines)
            let trimmed = line.trim();
            if !trimmed.is_empty() {
                current_sequence.extend_from_slice(trimmed.as_bytes());
            }
        }
    }
    
    // Process final sequence
    if in_sequence && !current_sequence.is_empty() {
        writer.write_all(&current_header)?;
        writer.write_all(b"\n")?;
        
        let rev_comp = reverse_complement(&current_sequence);
        write_fasta_sequence(&mut writer, &rev_comp, 60)?;
    }
    
    writer.flush()?;
    Ok(())
}

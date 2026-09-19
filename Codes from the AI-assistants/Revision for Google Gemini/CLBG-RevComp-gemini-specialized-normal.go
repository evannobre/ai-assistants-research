package main

import (
	"bufio"
	"bytes"
	"os"
)

// compTable acts as a constant-time Look-Up Table (LUT) for byte complements.
var compTable [256]byte

func init() {
	// Initialize default mappings
	for i := 0; i < 256; i++ {
		compTable[i] = byte(i)
	}

	// Map both uppercase and lowercase input to the uppercase complement
	complements := map[byte]byte{
		'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'U': 'A',
		'M': 'K', 'R': 'Y', 'W': 'W', 'S': 'S', 'Y': 'R',
		'K': 'M', 'V': 'B', 'H': 'D', 'D': 'H', 'B': 'V',
		'N': 'N',
	}

	for k, v := range complements {
		compTable[k] = v
		compTable[k+32] = v // lowercase ASCII offset
	}
}

func main() {
	// Use 1MB buffers for native I/O reading and writing to handle large streams efficiently.
	reader := bufio.NewReaderSize(os.Stdin, 1024*1024)
	writer := bufio.NewWriterSize(os.Stdout, 1024*1024)
	defer writer.Flush()

	var header []byte
	var seq []byte

	for {
		// Read line-by-line
		line, err := reader.ReadSlice('\n')
		
		// Handle the case where the file ends without a trailing newline
		isEOF := err != nil
		
		// Trim the newline/carriage return characters safely
		cleanLine := bytes.TrimRight(line, "\r\n")

		if len(cleanLine) > 0 {
			if cleanLine[0] == '>' {
				// If we already have a sequence in memory, process and flush it
				if len(header) > 0 {
					processSequence(header, seq, writer)
				}
				// Allocate new header, but reuse the underlying capacity for seq
				header = append([]byte{}, cleanLine...)
				seq = seq[:0] 
			} else {
				// Grow the data dynamically line-by-line as requested.
				// This relies on Go's internal slice doubling algorithm (amortized O(1)).
				seq = append(seq, cleanLine...)
			}
		}

		if isEOF {
			break
		}
	}

	// Process the final sequence block
	if len(header) > 0 {
		processSequence(header, seq, writer)
	}
}

// processSequence performs the reverse-complement in-place and writes to stdout
func processSequence(header, seq []byte, writer *bufio.Writer) {
	// 1. Write the header
	writer.Write(header)
	writer.WriteByte('\n')

	// 2. Reverse and complement the sequence using two-pointer approach
	i, j := 0, len(seq)-1
	for i <= j {
		// Lookup complements
		ci := compTable[seq[i]]
		cj := compTable[seq[j]]
		
		// Swap and overwrite in-place
		seq[i] = cj
		seq[j] = ci
		
		i++
		j--
	}

	// 3. Write output in standard 60-character FASTA wrap format
	const lineLen = 60
	for k := 0; k < len(seq); k += lineLen {
		end := k + lineLen
		if end > len(seq) {
			end = len(seq)
		}
		writer.Write(seq[k:end])
		writer.WriteByte('\n')
	}
}
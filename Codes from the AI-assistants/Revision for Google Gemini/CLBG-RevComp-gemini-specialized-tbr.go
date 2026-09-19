package main

import (
	"bufio"
	"bytes"
	"os"
)

// compTable provides an O(1) lookup for nucleotide complements.
var compTable [256]byte

func init() {
	// Initialize table with identical characters as fallback
	for i := 0; i < 256; i++ {
		compTable[i] = byte(i)
	}

	// Define the mapping based on IUPAC codes
	pairs := []string{
		"AT", "CG", "GC", "TA", "UA",
		"MK", "KM", "RY", "YR", "WW", "SS",
		"VB", "BV", "HD", "DH", "NN",
	}

	for _, pair := range pairs {
		base := pair[0]
		comp := pair[1]
		// Map uppercase
		compTable[base] = comp
		// Map lowercase to uppercase complement (ASCII offset 32)
		compTable[base+32] = comp
	}
}

func main() {
	// Buffered I/O reduces system calls and speeds up stream processing
	reader := bufio.NewReaderSize(os.Stdin, 128*1024)
	writer := bufio.NewWriterSize(os.Stdout, 128*1024)
	defer writer.Flush()

	var header []byte
	// sequence slice will dynamically grow (buffered-read by buffered-read)
	// We reuse this slice's capacity across sequences to minimize GC pressure.
	sequence := make([]byte, 0, 1024*1024) 

	for {
		line, err := reader.ReadSlice('\n')
		if err != nil {
			// If buffer limit is exceeded, ReadSlice returns bufio.ErrBufferFull.
			// ReadBytes handles lines larger than the 128KB buffer gracefully.
			if err == bufio.ErrBufferFull {
				fullLine, _ := reader.ReadBytes('\n')
				line = append(line, fullLine...)
			} else {
				// EOF or read error; process remaining buffer
				processSequence(writer, header, sequence)
				break
			}
		}

		// Strip carriage returns and newlines
		line = bytes.TrimRight(line, "\r\n")
		if len(line) == 0 {
			continue
		}

		if line[0] == '>' {
			// We hit a new sequence. Process the previous one (if any).
			if len(header) > 0 {
				processSequence(writer, header, sequence)
			}
			// Save the new header. We must copy it because `line` points to the reader's volatile buffer.
			header = append([]byte(nil), line...)
			// Reset the sequence length to 0, but crucially, KEEP the underlying capacity.
			sequence = sequence[:0]
		} else {
			// Dynamically grow the sequence. Go's append doubles capacity under the hood automatically.
			sequence = append(sequence, line...)
		}
	}
}

// processSequence reverses, complements, and writes out the sequence in 60-character lines.
func processSequence(writer *bufio.Writer, header []byte, seq []byte) {
	if len(header) == 0 {
		return
	}

	writer.Write(header)
	writer.WriteByte('\n')

	// In-place reverse and complement using two pointers
	i, j := 0, len(seq)-1
	for i <= j {
		seq[i], seq[j] = compTable[seq[j]], compTable[seq[i]]
		i++
		j--
	}

	// Write the sequence formatted to 60 columns (Standard FASTA formatting)
	for k := 0; k < len(seq); k += 60 {
		end := k + 60
		if end > len(seq) {
			end = len(seq)
		}
		writer.Write(seq[k:end])
		writer.WriteByte('\n')
	}
}
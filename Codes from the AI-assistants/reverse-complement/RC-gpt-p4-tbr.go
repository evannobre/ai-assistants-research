package main

import (
	"bufio"
	"bytes"
	"fmt"
	"io"
	"os"
)

const lineWidth = 60

func buildComplementTable() [256]byte {
	var c [256]byte

	// Default: identity (safe fallback; benchmark input is expected valid)
	for i := 0; i < 256; i++ {
		c[i] = byte(i)
	}

	// Uppercase IUPAC complements
	pairs := [][2]byte{
		{'A', 'T'},
		{'C', 'G'},
		{'G', 'C'},
		{'T', 'A'},
		{'U', 'A'},

		{'M', 'K'},
		{'R', 'Y'},
		{'W', 'W'},
		{'S', 'S'},
		{'Y', 'R'},
		{'K', 'M'},

		{'V', 'B'},
		{'H', 'D'},
		{'D', 'H'},
		{'B', 'V'},
		{'N', 'N'},
	}

	for _, p := range pairs {
		c[p[0]] = p[1]
	}

	// Lowercase versions
	for _, p := range pairs {
		loA := p[0] + ('a' - 'A')
		loB := p[1] + ('a' - 'A')
		c[loA] = loB
	}

	return c
}

func reverseComplementInPlace(seq []byte, comp *[256]byte) {
	i, j := 0, len(seq)-1
	for i < j {
		ai := seq[i]
		aj := seq[j]
		seq[i] = comp[aj]
		seq[j] = comp[ai]
		i++
		j--
	}
	if i == j && i >= 0 {
		seq[i] = comp[seq[i]]
	}
}

func writeWrapped(w *bufio.Writer, seq []byte) error {
	for len(seq) > 0 {
		n := lineWidth
		if len(seq) < n {
			n = len(seq)
		}
		if _, err := w.Write(seq[:n]); err != nil {
			return err
		}
		if err := w.WriteByte('\n'); err != nil {
			return err
		}
		seq = seq[n:]
	}
	return nil
}

func flushRecord(out *bufio.Writer, header []byte, seq []byte, comp *[256]byte) error {
	if len(header) == 0 {
		return nil
	}

	// Reverse-complement sequence in place
	reverseComplementInPlace(seq, comp)

	// Write header exactly as read
	if _, err := out.Write(header); err != nil {
		return err
	}

	// Write wrapped sequence
	return writeWrapped(out, seq)
}

func main() {
	in := bufio.NewReaderSize(os.Stdin, 1<<20)  // 1 MiB input buffer
	out := bufio.NewWriterSize(os.Stdout, 1<<20) // 1 MiB output buffer
	defer out.Flush()

	comp := buildComplementTable()

	var header []byte
	seq := make([]byte, 0, 1<<20) // start with 1 MiB capacity, grows as needed

	for {
		line, err := in.ReadBytes('\n')
		if len(line) > 0 {
			if line[0] == '>' {
				// New record begins: flush previous record (if any)
				if err2 := flushRecord(out, header, seq, &comp); err2 != nil {
					fmt.Fprintln(os.Stderr, "write error:", err2)
					os.Exit(1)
				}
				// Reset for new record
				header = append(header[:0], line...) // copy line
				seq = seq[:0]                        // keep capacity for reuse
			} else {
				// Sequence line: strip trailing newline and append
				line = bytes.TrimRight(line, "\r\n")
				seq = append(seq, line...)
			}
		}

		if err != nil {
			if err == io.EOF {
				// Flush last record at EOF
				if err2 := flushRecord(out, header, seq, &comp); err2 != nil {
					fmt.Fprintln(os.Stderr, "write error:", err2)
					os.Exit(1)
				}
				return
			}
			fmt.Fprintln(os.Stderr, "read error:", err)
			os.Exit(1)
		}
	}
}

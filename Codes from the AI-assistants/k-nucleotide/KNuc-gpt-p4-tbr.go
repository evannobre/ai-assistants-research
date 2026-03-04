package main

import (
	"bufio"
	"bytes"
	"fmt"
	"io"
	"os"
	"sort"
	"strings"
)

var enc [256]byte

func init() {
	// 2-bit encoding: A=0, C=1, G=2, T=3
	for i := range enc {
		enc[i] = 255
	}
	enc['A'], enc['a'] = 0, 0
	enc['C'], enc['c'] = 1, 1
	enc['G'], enc['g'] = 2, 2
	enc['T'], enc['t'] = 3, 3
}

// readSequenceThree reads all stdin, extracts FASTA record "THREE" (lines after >THREE ... until next > or EOF)
// and returns the raw bases as uppercase bytes (A/C/G/T).
func readSequenceThree(r io.Reader) ([]byte, error) {
	br := bufio.NewReaderSize(r, 1<<20) // 1MB buffer for fewer syscalls
	var seq bytes.Buffer
	inThree := false

	for {
		line, err := br.ReadBytes('\n')
		if len(line) > 0 {
			// Trim newline(s)
			line = bytes.TrimRight(line, "\r\n")
			if len(line) > 0 && line[0] == '>' {
				// Header line: check which record starts
				if bytes.HasPrefix(line, []byte(">THREE")) {
					inThree = true
				} else if inThree {
					// We were in THREE and a new record started -> done
					break
				} else {
					inThree = false
				}
			} else if inThree {
				// Sequence line: append, normalize to uppercase A/C/G/T
				for _, b := range line {
					switch b {
					case 'A', 'a', 'C', 'c', 'G', 'g', 'T', 't':
						seq.WriteByte(byte(strings.ToUpper(string([]byte{b}))[0]))
					default:
						// ignore anything else (shouldn't appear in THREE)
					}
				}
			}
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, err
		}
	}

	return seq.Bytes(), nil
}

func toCodes(seq []byte) []byte {
	codes := make([]byte, len(seq))
	for i, b := range seq {
		c := enc[b]
		// For THREE this should always be valid; keep it safe anyway.
		if c > 3 {
			c = 0
		}
		codes[i] = c
	}
	return codes
}

// packKmer packs k 2-bit codes into a uint64 (k <= 32 would fit; we need up to 18).
func packKmer(codes []byte) uint64 {
	var key uint64
	for _, c := range codes {
		key = (key << 2) | uint64(c)
	}
	return key
}

func unpackKmer(key uint64, k int) string {
	// decode from lowest bits backward
	out := make([]byte, k)
	for i := k - 1; i >= 0; i-- {
		switch key & 3 {
		case 0:
			out[i] = 'A'
		case 1:
			out[i] = 'C'
		case 2:
			out[i] = 'G'
		case 3:
			out[i] = 'T'
		}
		key >>= 2
	}
	return string(out)
}

// updateCountsForFrame updates the hash table for a particular reading frame (frame in [0..k-1]).
// It visits all start positions i where i % k == frame (i += k), and counts the k-mer at i.
func updateCountsForFrame(seqCodes []byte, k int, frame int, table map[uint64]uint32) {
	n := len(seqCodes)
	limit := n - k
	if limit < 0 {
		return
	}
	for i := frame; i <= limit; i += k {
		key := packKmer(seqCodes[i : i+k])
		table[key]++
	}
}

// countAllFrames counts all k-mers by combining all reading frames into a single hash table.
func countAllFrames(seqCodes []byte, k int) map[uint64]uint32 {
	// Grow from a small default size (per requirement).
	table := make(map[uint64]uint32, 1024)
	for frame := 0; frame < k; frame++ {
		updateCountsForFrame(seqCodes, k, frame, table)
	}
	return table
}

type freqItem struct {
	key   uint64
	count uint32
	code  string
}

func printFrequencies(seqCodes []byte, k int) {
	table := countAllFrames(seqCodes, k)
	total := float64(len(seqCodes) - k + 1)

	items := make([]freqItem, 0, len(table))
	for key, cnt := range table {
		items = append(items, freqItem{
			key:   key,
			count: cnt,
			code:  unpackKmer(key, k),
		})
	}

	sort.Slice(items, func(i, j int) bool {
		if items[i].count != items[j].count {
			return items[i].count > items[j].count // desc frequency
		}
		return items[i].code < items[j].code // asc key
	})

	w := bufio.NewWriterSize(os.Stdout, 1<<20)
	for _, it := range items {
		pct := 100.0 * float64(it.count) / total
		fmt.Fprintf(w, "%s %.3f\n", it.code, pct)
	}
	fmt.Fprintln(w)
	w.Flush()
}

func countOf(seqCodes []byte, fragment string) uint32 {
	k := len(fragment)
	// Build table for this k, then lookup.
	table := countAllFrames(seqCodes, k)
	fragCodes := make([]byte, k)
	for i := 0; i < k; i++ {
		fragCodes[i] = enc[fragment[i]]
	}
	key := packKmer(fragCodes)
	return table[key]
}

func main() {
	seq, err := readSequenceThree(os.Stdin)
	if err != nil {
		fmt.Fprintln(os.Stderr, "read error:", err)
		os.Exit(1)
	}
	seqCodes := toCodes(seq)

	// Frequencies
	printFrequencies(seqCodes, 1)
	printFrequencies(seqCodes, 2)

	// Specific sequences
	queries := []string{
		"GGT",
		"GGTA",
		"GGTATT",
		"GGTATTTTAATT",
		"GGTATTTTAATTTATAGT",
	}

	w := bufio.NewWriterSize(os.Stdout, 1<<20)
	for _, q := range queries {
		fmt.Fprintf(w, "%d\t%s\n", countOf(seqCodes, q), q)
	}
	w.Flush()
}

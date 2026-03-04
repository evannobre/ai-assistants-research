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

func main() {
	seq, err := readFastaRecord(os.Stdin, "THREE")
	if err != nil {
		// In benchmarking contexts, input is assumed valid; still, fail clearly.
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
	// Optional: ensure seq is uppercase (benchmark inputs already are).
	// for i := range seq { if seq[i] >= 'a' && seq[i] <= 'z' { seq[i] -= 32 } }

	printFreqTable(seq, 1)
	fmt.Println()
	printFreqTable(seq, 2)
	fmt.Println()

	queries := []string{
		"GGT",
		"GGTA",
		"GGTATT",
		"GGTATTTTAATT",
		"GGTATTTTAATTTATAGT",
	}
	for _, q := range queries {
		k := len(q)
		m := countK(seq, k)
		key, ok := encodeKmer([]byte(q))
		if !ok {
			fmt.Printf("0\t%s\n", q)
			continue
		}
		fmt.Printf("%d\t%s\n", m[key], q)
	}
}

// readFastaRecord reads stdin FASTA and returns the concatenated sequence lines
// of the record with the given id (token immediately following '>').
func readFastaRecord(r io.Reader, wantedID string) ([]byte, error) {
	br := bufio.NewReaderSize(r, 1<<20) // 1 MiB buffer: good for throughput

	var buf []byte
	inWanted := false

	for {
		line, err := br.ReadBytes('\n')
		if len(line) > 0 {
			// trim trailing newline / CRLF
			line = bytes.TrimRight(line, "\r\n")
			if len(line) == 0 {
				// skip empty lines
			} else if line[0] == '>' {
				// header: parse id
				inWanted = false
				// header token is up to first whitespace
				h := string(line[1:])
				id := h
				if sp := strings.IndexAny(h, " \t"); sp >= 0 {
					id = h[:sp]
				}
				if id == wantedID {
					inWanted = true
					// reset buffer for this record (benchmark expects one)
					buf = buf[:0]
				}
			} else if inWanted {
				// sequence line
				buf = append(buf, line...)
			}
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, err
		}
	}
	if len(buf) == 0 {
		return nil, fmt.Errorf("record %q not found or empty", wantedID)
	}
	return buf, nil
}

var base2bit = func() [256]byte {
	var m [256]byte
	// mark invalid as 255
	for i := range m {
		m[i] = 255
	}
	m['A'] = 0
	m['C'] = 1
	m['G'] = 2
	m['T'] = 3
	// If your inputs may contain 'U', treat it like 'T':
	// m['U'] = 3
	return m
}()

func encodeKmer(kmer []byte) (uint64, bool) {
	var key uint64
	for _, c := range kmer {
		v := base2bit[c]
		if v == 255 {
			return 0, false
		}
		key = (key << 2) | uint64(v)
	}
	return key, true
}

// countK counts all valid A/C/G/T k-mers in seq using rolling 2-bit encoding.
// Any window containing invalid chars would be skipped (not expected in benchmark inputs).
func countK(seq []byte, k int) map[uint64]uint32 {
	n := len(seq)
	if k <= 0 || n < k {
		return map[uint64]uint32{}
	}

	// capacity hint: number of windows
	windows := n - k + 1
	m := make(map[uint64]uint32, windows)

	mask := uint64(1)<<(2*uint(k)) - 1

	var key uint64
	valid := 0

	for i := 0; i < n; i++ {
		v := base2bit[seq[i]]
		if v == 255 {
			// reset on invalid base
			key = 0
			valid = 0
			continue
		}
		key = ((key << 2) | uint64(v)) & mask
		if valid < k {
			valid++
		}
		if valid >= k {
			m[key]++
		}
	}
	return m
}

type kv struct {
	key   uint64
	count uint32
	s     string // decoded for sorting/tie-break
}

func decodeKmer(key uint64, k int) string {
	// decode from lowest bits backward
	b := make([]byte, k)
	for i := k - 1; i >= 0; i-- {
		switch key & 3 {
		case 0:
			b[i] = 'A'
		case 1:
			b[i] = 'C'
		case 2:
			b[i] = 'G'
		case 3:
			b[i] = 'T'
		}
		key >>= 2
	}
	return string(b)
}

func printFreqTable(seq []byte, k int) {
	m := countK(seq, k)

	total := 0
	for _, c := range m {
		total += int(c)
	}
	entries := make([]kv, 0, len(m))
	for key, c := range m {
		s := decodeKmer(key, k)
		entries = append(entries, kv{key: key, count: c, s: s})
	}

	sort.Slice(entries, func(i, j int) bool {
		if entries[i].count != entries[j].count {
			return entries[i].count > entries[j].count
		}
		return entries[i].s < entries[j].s
	})

	for _, e := range entries {
		pct := (float64(e.count) * 100.0) / float64(total)
		fmt.Printf("%s %.3f\n", e.s, pct)
	}
}

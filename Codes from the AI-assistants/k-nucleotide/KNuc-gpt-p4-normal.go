package main

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"strings"
)

type kv struct {
	key   uint64
	count int
}

var decodeBase = [4]byte{'A', 'C', 'G', 'T'}

// A=0, C=1, G=2, T/U=3
func encodeBaseByte(b byte) byte {
	switch b {
	case 'A', 'a':
		return 0
	case 'C', 'c':
		return 1
	case 'G', 'g':
		return 2
	case 'T', 't', 'U', 'u':
		return 3
	default:
		// Benchmark input should be A/C/G/T, but we choose a safe fallback.
		return 0
	}
}

// Pack k bases (2 bits each) into uint64.
// For k up to 18, we need 36 bits, fits easily.
func encodeKmer(seq []byte, start, k int) uint64 {
	var key uint64 = 0
	for i := 0; i < k; i++ {
		key = (key << 2) | uint64(seq[start+i])
	}
	return key
}

func decodeKmer(key uint64, k int) string {
	out := make([]byte, k)
	for i := k - 1; i >= 0; i-- {
		out[i] = decodeBase[key&3]
		key >>= 2
	}
	return string(out)
}

// Required: update hash table counts for a PARTICULAR reading-frame.
// We then call it for all frames 0..k-1 to cover all start positions exactly once.
func updateFrameCounts(seq []byte, k, frame int, counts map[uint64]int) {
	n := len(seq)
	for i := frame; i+k <= n; i += k {
		key := encodeKmer(seq, i, k)
		counts[key] = counts[key] + 1
	}
}

func countAllFrames(seq []byte, k int) map[uint64]int {
	counts := make(map[uint64]int, 1024) // "grow from a small default size"
	for frame := 0; frame < k; frame++ {
		updateFrameCounts(seq, k, frame, counts)
	}
	return counts
}

func frequencyReport(seq []byte, k int) string {
	n := len(seq)
	if n < k {
		return "\n"
	}
	total := n - k + 1
	counts := countAllFrames(seq, k)

	items := make([]kv, 0, len(counts))
	for key, c := range counts {
		items = append(items, kv{key: key, count: c})
	}

	sort.Slice(items, func(i, j int) bool {
		if items[i].count != items[j].count {
			return items[i].count > items[j].count
		}
		// ascending key (lexicographic by decoded string matches ascending packed key
		// because we use fixed-width 2-bit encoding per character)
		return items[i].key < items[j].key
	})

	var sb strings.Builder
	for _, it := range items {
		pct := (100.0 * float64(it.count)) / float64(total)
		sb.WriteString(fmt.Sprintf("%s %.3f\n", decodeKmer(it.key, k), pct))
	}
	sb.WriteByte('\n')
	return sb.String()
}

func encodeLiteral(s string) (uint64, int) {
	k := len(s)
	tmp := make([]byte, k)
	for i := 0; i < k; i++ {
		tmp[i] = encodeBaseByte(s[i])
	}
	return encodeKmer(tmp, 0, k), k
}

func readSequenceThree() ([]byte, error) {
	in := bufio.NewReaderSize(os.Stdin, 1<<20) // 1MB buffer
	sc := bufio.NewScanner(in)

	// Allow long lines (FASTA generators can emit very long lines sometimes).
	// 64MB max token should be plenty for typical benchmark input.
	buf := make([]byte, 0, 1024*1024)
	sc.Buffer(buf, 64*1024*1024)

	inThree := false
	seq := make([]byte, 0, 1024*1024)

	for sc.Scan() {
		line := sc.Bytes()
		if len(line) == 0 {
			continue
		}
		if line[0] == '>' {
			// header line
			if inThree {
				// finished THREE when we hit next header
				break
			}
			// Check if this header is THREE
			// Accept forms like: >THREE ...description...
			if len(line) >= 6 && strings.HasPrefix(string(line[1:]), "THREE") {
				inThree = true
			}
			continue
		}

		if inThree {
			// append encoded bases from this sequence line
			for _, b := range line {
				seq = append(seq, encodeBaseByte(b))
			}
		}
	}

	if err := sc.Err(); err != nil {
		return nil, err
	}
	return seq, nil
}

func main() {
	seq, err := readSequenceThree()
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}

	// 1- and 2-nucleotide frequency tables
	fmt.Print(frequencyReport(seq, 1))
	fmt.Print(frequencyReport(seq, 2))

	// Specific k-mers
	targets := []string{
		"GGT",
		"GGTA",
		"GGTATT",
		"GGTATTTTAATT",
		"GGTATTTTAATTTATAGT",
	}

	for _, t := range targets {
		key, k := encodeLiteral(t)
		counts := countAllFrames(seq, k)
		fmt.Printf("%d\t%s\n", counts[key], t)
	}
}

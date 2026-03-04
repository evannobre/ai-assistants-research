package main

import (
	"bufio"
	"bytes"
	"fmt"
	"os"
	"sort"
)

func encBase(b byte) (uint64, bool) {
	switch b {
	case 'A', 'a':
		return 0, true
	case 'C', 'c':
		return 1, true
	case 'G', 'g':
		return 2, true
	case 'T', 't', 'U', 'u':
		return 3, true
	default:
		return 0, false
	}
}

func readThreeSequence() []byte {
	in := bufio.NewReaderSize(os.Stdin, 1<<20) // 1 MiB buffer
	var seq []byte
	seq = make([]byte, 0, 1<<20)

	var (
		inThree bool
		line    []byte
		err     error
	)

	for {
		line, err = in.ReadBytes('\n')
		if len(line) == 0 && err != nil {
			break
		}
		line = bytes.TrimRight(line, "\r\n")

		if len(line) > 0 && line[0] == '>' {
			// header line
			// target is ">THREE" (exact prefix match on ID)
			inThree = bytes.HasPrefix(line, []byte(">THREE"))
			continue
		}

		if inThree && len(line) > 0 {
			// append nucleotide line
			seq = append(seq, line...)
		}

		if err != nil {
			break
		}
	}
	return seq
}

func countKmers(seq []byte, k int) map[uint64]int {
	n := len(seq)
	if k <= 0 || n < k {
		return map[uint64]int{}
	}

	counts := make(map[uint64]int, n/2) // heuristic
	mask := uint64(1)<<(2*k) - 1

	var key uint64
	// build first window
	for i := 0; i < k; i++ {
		v, ok := encBase(seq[i])
		if !ok {
			// For benchmark inputs, this shouldn't happen.
			// If it does, treat as a hard break: no valid kmers.
			return map[uint64]int{}
		}
		key = (key << 2) | v
	}
	counts[key]++

	// roll
	for i := k; i < n; i++ {
		v, ok := encBase(seq[i])
		if !ok {
			return map[uint64]int{}
		}
		key = ((key << 2) & mask) | v
		counts[key]++
	}
	return counts
}

func keyToKmer(key uint64, k int) string {
	// decode from most-significant bits to least
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

type pair struct {
	s     string
	count int
}

func printFrequencies(seq []byte, k int, counts map[uint64]int) {
	total := len(seq) - k + 1
	ps := make([]pair, 0, len(counts))
	for key, c := range counts {
		ps = append(ps, pair{s: keyToKmer(key, k), count: c})
	}

	sort.Slice(ps, func(i, j int) bool {
		if ps[i].count != ps[j].count {
			return ps[i].count > ps[j].count
		}
		return ps[i].s < ps[j].s
	})

	w := bufio.NewWriterSize(os.Stdout, 1<<20)
	for _, p := range ps {
		pct := (float64(p.count) * 100.0) / float64(total)
		fmt.Fprintf(w, "%s %.3f\n", p.s, pct)
	}
	fmt.Fprintln(w)
	w.Flush()
}

func encodePattern(pat string) (uint64, bool) {
	var key uint64
	for i := 0; i < len(pat); i++ {
		v, ok := encBase(pat[i])
		if !ok {
			return 0, false
		}
		key = (key << 2) | v
	}
	return key, true
}

func main() {
	seq := readThreeSequence()

	// Compute only needed k values, cache them.
	neededKs := []int{1, 2, 3, 4, 6, 12, 18}
	cache := make(map[int]map[uint64]int, len(neededKs))
	for _, k := range neededKs {
		cache[k] = countKmers(seq, k)
	}

	// Output frequencies for k=1 and k=2
	printFrequencies(seq, 1, cache[1])
	printFrequencies(seq, 2, cache[2])

	// Output counts for specific patterns
	patterns := []string{
		"GGT",
		"GGTA",
		"GGTATT",
		"GGTATTTTAATT",
		"GGTATTTTAATTTATAGT",
	}

	w := bufio.NewWriterSize(os.Stdout, 1<<20)
	for _, pat := range patterns {
		k := len(pat)
		key, ok := encodePattern(pat)
		if !ok {
			fmt.Fprintf(w, "0\t%s\n", pat)
			continue
		}
		fmt.Fprintf(w, "%d\t%s\n", cache[k][key], pat)
	}
	w.Flush()
}

package main

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"strconv"
)

const (
	IM = 139968
	IA = 3877
	IC = 29573

	LINE = 60
)

// Naïve LCG state (classic Benchmarks Game constants).
type LCG struct {
	seed int
}

func (g *LCG) NextFloat() float64 {
	g.seed = (g.seed*IA + IC) % IM
	return float64(g.seed) / float64(IM)
}

type ProbTable struct {
	chars []byte
	cum   []float64 // cumulative probabilities
}

// Build cumulative distribution for binary search selection.
func NewProbTable(pairs []struct {
	ch byte
	p  float64
}) ProbTable {
	chars := make([]byte, len(pairs))
	cum := make([]float64, len(pairs))
	sum := 0.0
	for i, pr := range pairs {
		sum += pr.p
		chars[i] = pr.ch
		cum[i] = sum
	}
	// The benchmark data sums to 1.0 (or very close). Still, enforce last=1.0 to
	// avoid float edge cases causing out-of-range.
	cum[len(cum)-1] = 1.0
	return ProbTable{chars: chars, cum: cum}
}

func (t ProbTable) Pick(r float64) byte {
	// Find first index i where r < cum[i]
	i := sort.SearchFloat64s(t.cum, r)
	if i >= len(t.chars) {
		// Extremely unlikely with enforced cum[last]=1.0, but safe fallback.
		return t.chars[len(t.chars)-1]
	}
	return t.chars[i]
}

func writeHeader(w *bufio.Writer, name, desc string) {
	// FASTA header lines are typically: >NAME description
	_, _ = fmt.Fprintf(w, ">%s %s\n", name, desc)
}

func writeRepeat(w *bufio.Writer, seq []byte, total int) {
	// Writes "total" bytes by repeating seq, wrapped to LINE columns.
	// Streaming output: O(LINE) buffer.
	line := make([]byte, LINE)
	pos := 0 // position in seq

	for total > 0 {
		n := LINE
		if total < LINE {
			n = total
		}
		// Fill line[0:n] from seq, wrapping around.
		remain := n
		i := 0
		for remain > 0 {
			// copy as much as possible from current pos to end of seq
			chunk := len(seq) - pos
			if chunk > remain {
				chunk = remain
			}
			copy(line[i:i+chunk], seq[pos:pos+chunk])
			i += chunk
			pos += chunk
			remain -= chunk
			if pos == len(seq) {
				pos = 0
			}
		}
		_, _ = w.Write(line[:n])
		_ = w.WriteByte('\n')
		total -= n
	}
}

func writeRandom(w *bufio.Writer, g *LCG, table ProbTable, total int) {
	// Writes "total" random bases according to table, wrapped to LINE columns.
	line := make([]byte, LINE)

	for total > 0 {
		n := LINE
		if total < LINE {
			n = total
		}
		for i := 0; i < n; i++ {
			r := g.NextFloat()
			line[i] = table.Pick(r)
		}
		_, _ = w.Write(line[:n])
		_ = w.WriteByte('\n')
		total -= n
	}
}

func main() {
	// Benchmark convention: n from argv[1], default 1000.
	n := 1000
	if len(os.Args) > 1 {
		if v, err := strconv.Atoi(os.Args[1]); err == nil && v > 0 {
			n = v
		}
	}

	// Use a large output buffer to reduce syscalls.
	// 1–4 MiB is a good range; 1 MiB is safe and effective on 8 GB RAM.
	w := bufio.NewWriterSize(os.Stdout, 1<<20)
	defer w.Flush()

	alu := []byte(
		"GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG" +
			"GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA" +
			"CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT" +
			"ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA" +
			"GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG" +
			"AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC" +
			"AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA",
	)

	iub := NewProbTable([]struct {
		ch byte
		p  float64
	}{
		{'a', 0.27},
		{'c', 0.12},
		{'g', 0.12},
		{'t', 0.27},
		{'B', 0.02},
		{'D', 0.02},
		{'H', 0.02},
		{'K', 0.02},
		{'M', 0.02},
		{'N', 0.02},
		{'R', 0.02},
		{'S', 0.02},
		{'V', 0.02},
		{'W', 0.02},
		{'Y', 0.02},
	})

	homosapiens := NewProbTable([]struct {
		ch byte
		p  float64
	}{
		{'a', 0.3029549426680},
		{'c', 0.1979883004921},
		{'g', 0.1975473066391},
		{'t', 0.3015094502008},
	})

	rng := &LCG{seed: 42}

	writeHeader(w, "ONE", "Homo sapiens alu")
	writeRepeat(w, alu, 2*n)

	writeHeader(w, "TWO", "IUB ambiguity codes")
	writeRandom(w, rng, iub, 3*n)

	writeHeader(w, "THREE", "Homo sapiens frequency")
	writeRandom(w, rng, homosapiens, 5*n)
}

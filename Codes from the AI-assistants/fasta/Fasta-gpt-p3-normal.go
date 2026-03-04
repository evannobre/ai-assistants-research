// FASTA simulation using naive LCG and naive cumulative-probability matching.
// Ubuntu 24.04-friendly, standard library only, streaming output (low RAM).
//
// Usage:
//   go run fasta.go 1000
//   go run fasta.go 25000000 > out.fasta

package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

const (
	lineLen = 60

	IM uint32 = 139968
	IA uint32 = 3877
	IC uint32 = 29573
)

var seed uint32 = 42

// ALU sequence used by the Benchmarks Game FASTA problem.
const alu = "" +
	"GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG" +
	"GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA" +
	"CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT" +
	"ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA" +
	"GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG" +
	"AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC" +
	"AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"

// Weighted symbol for random FASTA.
type weighted struct {
	sym byte
	p   float64 // probability
}

type cumulativeTable struct {
	syms []byte
	cum  []float64 // same length as syms, strictly increasing up to ~1.0
}

// makeCumulative converts expected probabilities into cumulative probabilities.
// IMPORTANT: No scaling to integers; keep float64 cumulative probabilities.
func makeCumulative(items []weighted) cumulativeTable {
	syms := make([]byte, len(items))
	cum := make([]float64, len(items))

	var running float64
	for i, it := range items {
		running += it.p
		syms[i] = it.sym
		cum[i] = running
	}
	return cumulativeTable{syms: syms, cum: cum}
}

// nextRandom returns a float64 in [0,1) using the naive LCG.
// IMPORTANT: Must be called once per nucleotide selection; no caching.
func nextRandom() float64 {
	seed = (seed*IA + IC) % IM
	return float64(seed) / float64(IM) // Max = 1.0
}

// pickSymbol matches r against cumulative probabilities to select a symbol.
// IMPORTANT: Do not optimize; use linear scan (or binary search). Here: linear scan.
func pickSymbol(tab cumulativeTable, r float64) byte {
	for i, c := range tab.cum {
		if r < c {
			return tab.syms[i]
		}
	}
	// Fallback for any floating rounding edge case:
	return tab.syms[len(tab.syms)-1]
}

// writeWrapped writes exactly n bases, inserting '\n' every 60 characters.
func writeWrapped(w *bufio.Writer, gen func() byte, n int) error {
	buf := make([]byte, 0, lineLen+1)

	for n > 0 {
		chunk := lineLen
		if n < lineLen {
			chunk = n
		}

		buf = buf[:0]
		for i := 0; i < chunk; i++ {
			buf = append(buf, gen())
		}
		buf = append(buf, '\n')

		if _, err := w.Write(buf); err != nil {
			return err
		}
		n -= chunk
	}
	return nil
}

// repeatFasta copies from a given sequence (cyclically) to produce n bases.
func repeatFasta(w *bufio.Writer, header string, seq string, n int) error {
	if _, err := fmt.Fprintln(w, header); err != nil {
		return err
	}

	s := []byte(seq)
	pos := 0
	gen := func() byte {
		b := s[pos]
		pos++
		if pos == len(s) {
			pos = 0
		}
		return b
	}
	return writeWrapped(w, gen, n)
}

// randomFasta generates n bases by weighted random selection from an alphabet.
func randomFasta(w *bufio.Writer, header string, tab cumulativeTable, n int) error {
	if _, err := fmt.Fprintln(w, header); err != nil {
		return err
	}

	gen := func() byte {
		r := nextRandom()
		return pickSymbol(tab, r)
	}
	return writeWrapped(w, gen, n)
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: fasta <n>")
		os.Exit(2)
	}
	n64, err := strconv.ParseInt(os.Args[1], 10, 32)
	if err != nil || n64 < 0 {
		fmt.Fprintln(os.Stderr, "n must be a non-negative 32-bit integer")
		os.Exit(2)
	}
	n := int(n64)

	// Alphabet #1: IUB ambiguity codes (as used in the benchmark).
	iub := []weighted{
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
	}

	// Alphabet #2: Homo sapiens frequencies (as used in the benchmark).
	homo := []weighted{
		{'a', 0.3029549426680},
		{'c', 0.1979883004921},
		{'g', 0.1975473066391},
		{'t', 0.3015094502008},
	}

	iubTab := makeCumulative(iub)
	homoTab := makeCumulative(homo)

	w := bufio.NewWriterSize(os.Stdout, 1<<20) // 1 MiB buffer to reduce syscalls
	defer w.Flush()

	// Required outputs: 2n, 3n, 5n
	if err := repeatFasta(w, ">ONE Homo sapiens alu", alu, 2*n); err != nil {
		fmt.Fprintln(os.Stderr, "write error:", err)
		os.Exit(1)
	}
	if err := randomFasta(w, ">TWO IUB ambiguity codes", iubTab, 3*n); err != nil {
		fmt.Fprintln(os.Stderr, "write error:", err)
		os.Exit(1)
	}
	if err := randomFasta(w, ">THREE Homo sapiens frequency", homoTab, 5*n); err != nil {
		fmt.Fprintln(os.Stderr, "write error:", err)
		os.Exit(1)
	}
}

package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

const (
	lineLen = 60

	// Naïve LCG constants (must match spec)
	IM   = 139968
	IA   = 3877
	IC   = 29573
	Seed = 42
)

// rng implements the required naïve LCG:
//   seed = (seed*IA + IC) mod IM
//   return Max * seed / IM
// We use Max = 1.0 and return seed/IM in [0,1).
type rng struct {
	seed int
}

func newRNG() *rng {
	return &rng{seed: Seed}
}

func (r *rng) nextFloat() float64 {
	// Keep it “naïve”: direct arithmetic, no caching, no vectorization, etc.
	r.seed = (r.seed*IA + IC) % IM
	return float64(r.seed) / float64(IM)
}

type weightedAlphabet struct {
	symbols []byte
	cumProb []float64 // cumulative probabilities, increasing, last should be ~1.0
}

func newWeightedAlphabet(pairs []struct {
	ch   byte
	prob float64
}) weightedAlphabet {
	symbols := make([]byte, len(pairs))
	cum := make([]float64, len(pairs))
	sum := 0.0
	for i, p := range pairs {
		sum += p.prob
		symbols[i] = p.ch
		cum[i] = sum
	}
	return weightedAlphabet{symbols: symbols, cumProb: cum}
}

// selectByLinearSearch matches r against cumulative probabilities using linear search.
func (wa weightedAlphabet) selectByLinearSearch(r float64) byte {
	for i, cp := range wa.cumProb {
		if r < cp {
			return wa.symbols[i]
		}
	}
	// In case of tiny floating rounding, fall back to last symbol.
	return wa.symbols[len(wa.symbols)-1]
}

// writeRepeated writes `total` chars by repeating `base`, wrapped to 60 columns.
func writeRepeated(w *bufio.Writer, base string, total int) error {
	baseBytes := []byte(base)
	baseLen := len(baseBytes)
	if baseLen == 0 || total <= 0 {
		return nil
	}

	col := 0
	idx := 0
	for i := 0; i < total; i++ {
		if _, err := w.Write([]byte{baseBytes[idx]}); err != nil {
			return err
		}
		idx++
		if idx == baseLen {
			idx = 0
		}

		col++
		if col == lineLen {
			if err := w.WriteByte('\n'); err != nil {
				return err
			}
			col = 0
		}
	}
	if col != 0 {
		return w.WriteByte('\n')
	}
	return nil
}

// writeRandomWeighted writes `total` chars selected by weighted random selection.
func writeRandomWeighted(w *bufio.Writer, r *rng, wa weightedAlphabet, total int) error {
	if total <= 0 {
		return nil
	}

	col := 0
	for i := 0; i < total; i++ {
		// Must call LCG every time a nucleotide is selected (no caching).
		x := r.nextFloat()
		ch := wa.selectByLinearSearch(x)

		if _, err := w.Write([]byte{ch}); err != nil {
			return err
		}

		col++
		if col == lineLen {
			if err := w.WriteByte('\n'); err != nil {
				return err
			}
			col = 0
		}
	}
	if col != 0 {
		return w.WriteByte('\n')
	}
	return nil
}

func main() {
	// Default n if not provided, but Benchmarks Game style expects one arg.
	n := 1000
	if len(os.Args) > 1 {
		if v, err := strconv.Atoi(os.Args[1]); err == nil && v > 0 {
			n = v
		}
	}

	// Fixed ALU sequence (Benchmarks Game fasta)
	const alu = "" +
		"GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG" +
		"GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA" +
		"CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT" +
		"ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA" +
		"GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG" +
		"AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC" +
		"AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"

	// IUB ambiguity codes (Benchmarks Game fasta)
	iub := newWeightedAlphabet([]struct {
		ch   byte
		prob float64
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

	// Homo sapiens nucleotide frequencies (Benchmarks Game fasta)
	homosapiens := newWeightedAlphabet([]struct {
		ch   byte
		prob float64
	}{
		{'a', 0.3029549426680},
		{'c', 0.1979883004921},
		{'g', 0.1975473066391},
		{'t', 0.3015094502008},
	})

	out := bufio.NewWriterSize(os.Stdout, 1<<20) // 1 MiB buffer for throughput
	defer out.Flush()

	r := newRNG()

	// Section 1: repeated copy, length 2*n
	fmt.Fprintln(out, ">ONE Homo sapiens alu")
	if err := writeRepeated(out, alu, 2*n); err != nil {
		fmt.Fprintln(os.Stderr, "write error:", err)
		os.Exit(1)
	}

	// Section 2: weighted random (IUB), length 3*n
	fmt.Fprintln(out, ">TWO IUB ambiguity codes")
	if err := writeRandomWeighted(out, r, iub, 3*n); err != nil {
		fmt.Fprintln(os.Stderr, "write error:", err)
		os.Exit(1)
	}

	// Section 3: weighted random (Homo sapiens), length 5*n
	fmt.Fprintln(out, ">THREE Homo sapiens frequency")
	if err := writeRandomWeighted(out, r, homosapiens, 5*n); err != nil {
		fmt.Fprintln(os.Stderr, "write error:", err)
		os.Exit(1)
	}
}

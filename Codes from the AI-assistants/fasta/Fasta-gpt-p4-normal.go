package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

const (
	lineLen = 60

	IM = 139968
	IA = 3877
	IC = 29573
)

var seed int = 42

// Naïve LCG: update seed every time you need a random number.
// Returns r in [0,1).
func nextRand() float64 {
	seed = (seed*IA + IC) % IM
	return float64(seed) / float64(IM)
}

type WeightedAlphabet struct {
	symbols []byte
	cumProb []float64 // cumulative probabilities
}

// Build cumulative probabilities from expected probabilities.
// No scaling factors; just running float sums.
func newWeightedAlphabet(symbols []byte, probs []float64) WeightedAlphabet {
	cum := make([]float64, len(probs))
	sum := 0.0
	for i, p := range probs {
		sum += p
		cum[i] = sum
	}
	return WeightedAlphabet{symbols: symbols, cumProb: cum}
}

// Naïve lookup: linear search over cumulative probabilities.
func (wa WeightedAlphabet) pick(r float64) byte {
	for i, cp := range wa.cumProb {
		if r < cp {
			return wa.symbols[i]
		}
	}
	// In case of tiny float rounding pushing r to the end, return last symbol.
	return wa.symbols[len(wa.symbols)-1]
}

// Write a FASTA header line.
func writeHeader(w *bufio.Writer, header string) {
	// header already includes leading '>'
	fmt.Fprintln(w, header)
}

// Write repeated sequence (cyclic copy) to length n, wrapped at 60 chars/line.
func writeRepeated(w *bufio.Writer, seq string, n int) {
	if n <= 0 {
		return
	}
	b := []byte(seq)
	L := len(b)

	pos := 0
	for n > 0 {
		chunk := lineLen
		if n < chunk {
			chunk = n
		}

		// Build one line.
		line := make([]byte, chunk+1)
		for i := 0; i < chunk; i++ {
			line[i] = b[pos]
			pos++
			if pos == L {
				pos = 0
			}
		}
		line[chunk] = '\n'
		w.Write(line)

		n -= chunk
	}
}

// Write random sequence according to weighted alphabet, length n, wrapped at 60 chars/line.
// Uses naïve LCG *per nucleotide* (no caching).
func writeRandom(w *bufio.Writer, wa WeightedAlphabet, n int) {
	if n <= 0 {
		return
	}
	for n > 0 {
		chunk := lineLen
		if n < chunk {
			chunk = n
		}

		line := make([]byte, chunk+1)
		for i := 0; i < chunk; i++ {
			r := nextRand()
			line[i] = wa.pick(r)
		}
		line[chunk] = '\n'
		w.Write(line)

		n -= chunk
	}
}

func main() {
	n := 0
	if len(os.Args) > 1 {
		if v, err := strconv.Atoi(os.Args[1]); err == nil && v > 0 {
			n = v
		}
	}

	// Standard FASTA benchmark inputs.
	const alu = "" +
		"GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG" +
		"GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA" +
		"CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT" +
		"ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA" +
		"GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG" +
		"AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC" +
		"AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"

	// IUB ambiguity codes (15).
	iubSymbols := []byte("acgtBDHKMNRSVWY")
	iubProbs := []float64{
		0.27, 0.12, 0.12, 0.27,
		0.02, 0.02, 0.02, 0.02, 0.02,
		0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
	}
	iub := newWeightedAlphabet(iubSymbols, iubProbs)

	// Homo sapiens frequency (4).
	hsSymbols := []byte("acgt")
	hsProbs := []float64{0.3029549426680, 0.1979883004921, 0.1975473066391, 0.3015094502008}
	hs := newWeightedAlphabet(hsSymbols, hsProbs)

	// Big buffered output (streaming, memory-safe).
	// You can increase/decrease; 1–8MB is usually fine.
	out := bufio.NewWriterSize(os.Stdout, 1<<20)
	defer out.Flush()

	writeHeader(out, ">ONE Homo sapiens alu")
	writeRepeated(out, alu, 2*n)

	writeHeader(out, ">TWO IUB ambiguity codes")
	writeRandom(out, iub, 3*n)

	writeHeader(out, ">THREE Homo sapiens frequency")
	writeRandom(out, hs, 5*n)
}

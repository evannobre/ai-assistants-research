package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

// Naïve LCG Constants as requested
const (
	im = 139968
	ia = 3877
	ic = 29573
)

// Global state for our LCG seed
var seed = 42

// Nucleotide represents a DNA character and its selection probability
type Nucleotide struct {
	Char        byte
	Probability float64
}

// Data Sets
var (
	alu = []byte("GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGATCACCTGAGG" +
		"TCAGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAATACAAAAATTAGCCGGG" +
		"CGTGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGGAGGC" +
		"GGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA")

	iub = []Nucleotide{
		{'a', 0.27}, {'c', 0.12}, {'g', 0.12}, {'t', 0.27},
		{'B', 0.02}, {'D', 0.02}, {'H', 0.02}, {'K', 0.02},
		{'M', 0.02}, {'N', 0.02}, {'R', 0.02}, {'S', 0.02},
		{'V', 0.02}, {'W', 0.02}, {'Y', 0.02},
	}

	homosapiens = []Nucleotide{
		{'a', 0.3029549426680},
		{'c', 0.1979883004921},
		{'g', 0.1975473066391},
		{'t', 0.3015094502008},
	}
)

// makeCumulative converts individual probabilities into cumulative probabilities
func makeCumulative(nucleotides []Nucleotide) []Nucleotide {
	var cp float64 = 0.0
	cumulative := make([]Nucleotide, len(nucleotides))
	for i, nuc := range nucleotides {
		cp += nuc.Probability
		cumulative[i] = Nucleotide{
			Char:        nuc.Char,
			Probability: cp,
		}
	}
	return cumulative
}

// genRandom implements the naïve LCG algorithm
func genRandom(max float64) float64 {
	seed = (seed*ia + ic) % im
	return max * float64(seed) / float64(im)
}

// selectRandom uses a linear search to match the LCG float against cumulative probabilities
func selectRandom(cumulative []Nucleotide) byte {
	r := genRandom(1.0)
	for _, nuc := range cumulative {
		if r < nuc.Probability {
			return nuc.Char
		}
	}
	// Fallback to the last character due to floating-point rounding margins
	return cumulative[len(cumulative)-1].Char
}

// makeRepeatFasta generates a sequence by repeating a given byte array
func makeRepeatFasta(writer *bufio.Writer, id, desc string, sequence []byte, n int) {
	fmt.Fprintf(writer, ">%s %s\n", id, desc)
	seqLen := len(sequence)
	pos := 0

	for n > 0 {
		lineLen := 60
		if n < lineLen {
			lineLen = n
		}
		
		for i := 0; i < lineLen; i++ {
			writer.WriteByte(sequence[pos])
			pos = (pos + 1) % seqLen
		}
		writer.WriteByte('\n')
		n -= lineLen
	}
}

// makeRandomFasta generates a sequence using weighted random selection
func makeRandomFasta(writer *bufio.Writer, id, desc string, table []Nucleotide, n int) {
	fmt.Fprintf(writer, ">%s %s\n", id, desc)
	
	// Pre-calculate cumulative probabilities
	cumulativeTable := makeCumulative(table)

	for n > 0 {
		lineLen := 60
		if n < lineLen {
			lineLen = n
		}

		for i := 0; i < lineLen; i++ {
			writer.WriteByte(selectRandom(cumulativeTable))
		}
		writer.WriteByte('\n')
		n -= lineLen
	}
}

func main() {
	// Parse n from command-line arguments, default to 1000 if not provided
	n := 1000
	if len(os.Args) > 1 {
		if parsed, err := strconv.Atoi(os.Args[1]); err == nil {
			n = parsed
		}
	}

	// We use bufio.Writer to minimize system calls and optimize disk writes for large n.
	// We are relying entirely on the native standard library ("os", "bufio").
	writer := bufio.NewWriter(os.Stdout)
	defer writer.Flush()

	makeRepeatFasta(writer, "ONE", "Homo sapiens alu", alu, n*2)
	makeRandomFasta(writer, "TWO", "IUB ambiguity codes", iub, n*3)
	makeRandomFasta(writer, "THREE", "Homo sapiens frequency", homosapiens, n*5)
}
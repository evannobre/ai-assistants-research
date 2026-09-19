package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

const (
	im         = 139968
	ia         = 3877
	ic         = 29573
	lineLength = 60
)

var seed = int32(42)

// Nucleotide represents a character and its probability
type Nucleotide struct {
	Char byte
	Prob float64
}

// nextRandom implements the naïve LCG algorithm
func nextRandom() float64 {
	seed = (seed*ia + ic) % im
	return float64(seed) / float64(im)
}

// makeCumulative converts expected probabilities into a cumulative distribution
func makeCumulative(table []Nucleotide) {
	cumulative := 0.0
	for i := range table {
		cumulative += table[i].Prob
		table[i].Prob = cumulative
	}
}

// repeatFasta copies from a given sequence cyclically
func repeatFasta(out *bufio.Writer, title string, sequence string, n int) {
	out.WriteString(title + "\n")
	seqLen := len(sequence)
	pos := 0

	for n > 0 {
		line := lineLength
		if n < lineLength {
			line = n
		}
		
		for i := 0; i < line; i++ {
			out.WriteByte(sequence[pos])
			pos++
			if pos >= seqLen {
				pos = 0
			}
		}
		out.WriteByte('\n')
		n -= line
	}
}

// randomFasta generates DNA sequences by weighted random selection
func randomFasta(out *bufio.Writer, title string, table []Nucleotide, n int) {
	out.WriteString(title + "\n")
	makeCumulative(table)

	for n > 0 {
		line := lineLength
		if n < lineLength {
			line = n
		}
		
		for i := 0; i < line; i++ {
			p := nextRandom()
			// Linear search against cumulative probabilities
			for _, nuc := range table {
				if p < nuc.Prob {
					out.WriteByte(nuc.Char)
					break
				}
			}
		}
		out.WriteByte('\n')
		n -= line
	}
}

func main() {
	n := 1000 // Default value
	if len(os.Args) > 1 {
		if val, err := strconv.Atoi(os.Args[1]); err == nil {
			n = val
		}
	}

	// Buffer the standard output to optimize SSD writes and minimize syscalls
	// A 64KB buffer is highly efficient for most Linux file systems.
	out := bufio.NewWriterSize(os.Stdout, 64*1024)
	defer out.Flush() // Ensure all buffered data is written before exit

	alu := "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAATACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"

	iub := []Nucleotide{
		{'a', 0.27}, {'c', 0.12}, {'g', 0.12}, {'t', 0.27},
		{'B', 0.02}, {'D', 0.02}, {'H', 0.02}, {'K', 0.02},
		{'M', 0.02}, {'N', 0.02}, {'R', 0.02}, {'S', 0.02},
		{'V', 0.02}, {'W', 0.02}, {'Y', 0.02},
	}

	homoSapiens := []Nucleotide{
		{'a', 0.3029549426680},
		{'c', 0.1979883004921},
		{'g', 0.1975473066391},
		{'t', 0.3015094502008},
	}

	// Execute the three required FASTA benchmark sequences
	repeatFasta(out, ">ONE Homo sapiens alu", alu, n*2)
	randomFasta(out, ">TWO IUB ambiguity codes", iub, n*3)
	randomFasta(out, ">THREE Homo sapiens frequency", homoSapiens, n*5)
}
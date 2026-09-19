package main

import (
	"bufio"
	"bytes"
	"fmt"
	"io"
	"os"
	"sort"
)

// Mapping DNA nucleotides to 2-bit values.
// T is mapped to 3, G to 2, C to 1, A to 0 to maintain alphabetical sorting naturally
// when comparing raw bits, though we rely on explicit string comparison later.
var charToNum = [256]uint64{
	'A': 0, 'a': 0,
	'C': 1, 'c': 1,
	'G': 2, 'g': 2,
	'T': 3, 't': 3,
}

var numToChar = []byte{'A', 'C', 'G', 'T'}

// pack converts a byte slice of DNA into a single uint64 key.
func pack(seq []byte) uint64 {
	var key uint64
	for _, b := range seq {
		key = (key << 2) | charToNum[b]
	}
	return key
}

// unpack converts a 64-bit key back to a DNA string of the specified length.
func unpack(key uint64, length int) string {
	res := make([]byte, length)
	for i := length - 1; i >= 0; i-- {
		res[i] = numToChar[key&3]
		key >>= 2
	}
	return string(res)
}

// extractSequenceThree reads FASTA format from stdin and extracts only sequence THREE.
func extractSequenceThree() []byte {
	reader := bufio.NewReader(os.Stdin)
	var seq []byte
	inSequenceThree := false

	for {
		line, err := reader.ReadSlice('\n')
		if err != nil && err != io.EOF {
			break
		}

		if len(line) > 0 && line[0] == '>' {
			if bytes.HasPrefix(line, []byte(">THREE")) {
				inSequenceThree = true
			} else if inSequenceThree {
				// We've hit the next sequence, so we can stop reading.
				break
			}
		} else if inSequenceThree {
			// Fast path to strip newlines and append to our sequence slice
			line = bytes.TrimSpace(line)
			seq = append(seq, bytes.ToUpper(line)...)
		}

		if err == io.EOF {
			break
		}
	}
	return seq
}

// countKmers implements the sliding window algorithm to populate the native map.
func countKmers(seq []byte, k int) map[uint64]int {
	counts := make(map[uint64]int)
	if len(seq) < k {
		return counts
	}

	// mask is used to strip out the highest bits when the window slides
	mask := uint64(1<<(2*k) - 1)
	var currentKey uint64

	// Prime the window for the first k-1 nucleotides
	for i := 0; i < k-1; i++ {
		currentKey = (currentKey << 2) | charToNum[seq[i]]
	}

	// Slide the window across the sequence
	for i := k - 1; i < len(seq); i++ {
		currentKey = ((currentKey << 2) & mask) | charToNum[seq[i]]
		counts[currentKey]++
	}

	return counts
}

type kmerFreq struct {
	kmer  string
	count int
}

// printFrequencies calculates percentages and sorts the outputs as requested.
func printFrequencies(seq []byte, k int) {
	counts := countKmers(seq, k)
	totalKmers := len(seq) - k + 1

	var list []kmerFreq
	for key, count := range counts {
		list = append(list, kmerFreq{kmer: unpack(key, k), count: count})
	}

	// Sort by descending frequency, then ascending k-nucleotide key
	sort.Slice(list, func(i, j int) bool {
		if list[i].count == list[j].count {
			return list[i].kmer < list[j].kmer
		}
		return list[i].count > list[j].count
	})

	for _, item := range list {
		percentage := float64(item.count) * 100.0 / float64(totalKmers)
		fmt.Printf("%s %.3f\n", item.kmer, percentage)
	}
	fmt.Println()
}

// printSpecificCount retrieves the count for a specific requested sequence.
func printSpecificCount(seq []byte, target string) {
	k := len(target)
	counts := countKmers(seq, k)
	targetKey := pack([]byte(target))
	fmt.Printf("%d\t%s\n", counts[targetKey], target)
}

func main() {
	seq := extractSequenceThree()

	// 1. Count 1- and 2-nucleotide sequences and print frequencies
	printFrequencies(seq, 1)
	printFrequencies(seq, 2)

	// 2. Count specific lengths and write the count for specific sequences
	targets := []string{"GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"}
	for _, target := range targets {
		printSpecificCount(seq, target)
	}
}
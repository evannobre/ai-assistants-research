package main

import (
	"bufio"
	"bytes"
	"fmt"
	"os"
	"sort"
)

var toNum [256]uint64
var toChar = []byte{'A', 'C', 'G', 'T'}

// Initialize the lookup table for fast byte-to-integer conversion.
func init() {
	toNum['A'] = 0; toNum['a'] = 0
	toNum['C'] = 1; toNum['c'] = 1
	toNum['G'] = 2; toNum['g'] = 2
	toNum['T'] = 3; toNum['t'] = 3
}

// pack converts a DNA sequence byte slice into a compact uint64 representation.
func pack(seq []byte) uint64 {
	var val uint64
	for _, b := range seq {
		val = (val << 2) | toNum[b]
	}
	return val
}

// unpack reverses the bit-packing, converting a uint64 back to a DNA string.
func unpack(val uint64, k int) string {
	b := make([]byte, k)
	for i := k - 1; i >= 0; i-- {
		b[i] = toChar[val&3]
		val >>= 2
	}
	return string(b)
}

// updateFrame updates the hash table for a specific reading-frame.
// It skips by 'k' to ensure we only count non-overlapping sequences for this specific frame.
func updateFrame(seq []byte, k int, frame int, counts map[uint64]int) {
	for i := frame; i <= len(seq)-k; i += k {
		val := pack(seq[i : i+k])
		counts[val]++
	}
}

// countAllFrames creates the hash table, growing it from a default small size,
// and combines the k-nucleotide counts for all reading-frames.
func countAllFrames(seq []byte, k int) map[uint64]int {
	// Built-in map initializes with a small capacity and grows dynamically
	counts := make(map[uint64]int) 
	for frame := 0; frame < k; frame++ {
		updateFrame(seq, k, frame, counts)
	}
	return counts
}

// printFreqs calculates percentages, sorts by frequency (desc) then by key (asc), and prints.
func printFreqs(counts map[uint64]int, k int) {
	type kv struct {
		seq   string
		count int
	}
	var total int
	var arr []kv

	for val, count := range counts {
		arr = append(arr, kv{unpack(val, k), count})
		total += count
	}

	// Sort by descending frequency, then ascending string key
	sort.Slice(arr, func(i, j int) bool {
		if arr[i].count == arr[j].count {
			return arr[i].seq < arr[j].seq
		}
		return arr[i].count > arr[j].count
	})

	for _, item := range arr {
		fmt.Printf("%s %.3f\n", item.seq, float64(item.count)*100/float64(total))
	}
	fmt.Println()
}

func main() {
	scanner := bufio.NewScanner(os.Stdin)

	// 1. Skip until we find the >THREE DNA sequence
	for scanner.Scan() {
		if bytes.HasPrefix(scanner.Bytes(), []byte(">THREE")) {
			break
		}
	}

	// 2. Extract DNA sequence THREE into memory
	var buf bytes.Buffer
	for scanner.Scan() {
		line := scanner.Bytes()
		if len(line) == 0 {
			continue
		}
		if line[0] == '>' {
			break // Reached the next sequence, stop reading
		}
		// scanner.Bytes() automatically strips the newline
		buf.Write(line)
	}
	seq := buf.Bytes()

	// 3. Count 1-nucleotide and 2-nucleotide sequences and print frequency %
	printFreqs(countAllFrames(seq, 1), 1)
	printFreqs(countAllFrames(seq, 2), 2)

	// 4. Count and print specific longer target sequences
	targets := []string{
		"GGT",
		"GGTA",
		"GGTATT",
		"GGTATTTTAATT",
		"GGTATTTTAATTTATAGT",
	}

	for _, t := range targets {
		k := len(t)
		// We use the exact same algorithm to calculate these results without skipping work
		counts := countAllFrames(seq, k)
		packedTarget := pack([]byte(t))
		fmt.Printf("%d\t%s\n", counts[packedTarget], t)
	}
}
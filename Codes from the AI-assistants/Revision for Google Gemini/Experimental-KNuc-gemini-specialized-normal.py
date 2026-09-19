package main

import (
	"bufio"
	"bytes"
	"fmt"
	"log"
	"os"
	"sort"
)

// countKmers slides a window of size k across the sequence.
// It uses Go's native map as the hash table.
func countKmers(seq string, k int) map[string]int {
	counts := make(map[string]int)
	
	// Boundary check to prevent index out of range
	if len(seq) < k {
		return counts
	}

	// Slicing seq[i:i+k] in Go does not allocate new memory;
	// it simply creates a string header pointing to the original data.
	for i := 0; i <= len(seq)-k; i++ {
		counts[seq[i:i+k]]++
	}
	return counts
}

// readSequence extracts the target FASTA sequence into a single string.
func readSequence(filename string, prefix string) (string, error) {
	file, err := os.Open(filename)
	if err != nil {
		return "", err
	}
	defer file.Close()

	// 1MB buffer to optimize SSD reads
	scanner := bufio.NewScanner(file)
	buf := make([]byte, 1024*1024)
	scanner.Buffer(buf, 1024*1024)

	var data bytes.Buffer
	inSequence := false

	for scanner.Scan() {
		line := scanner.Bytes()
		if len(line) == 0 {
			continue
		}

		// Handle FASTA headers
		if line[0] == '>' {
			if inSequence {
				break // Stop reading if we hit the next sequence
			}
			if bytes.HasPrefix(line, []byte(prefix)) {
				inSequence = true
			}
			continue
		}

		if inSequence {
			data.Write(bytes.ToUpper(line))
		}
	}

	if err := scanner.Err(); err != nil {
		return "", err
	}

	return data.String(), nil
}

// printFrequencies sorts and prints the frequencies of k-mers.
func printFrequencies(counts map[string]int) {
	var total int
	for _, v := range counts {
		total += v
	}

	// Struct to hold key-value pairs for sorting
	type kv struct {
		kmer  string
		count int
	}

	var sorted []kv
	for k, v := range counts {
		sorted = append(sorted, kv{k, v})
	}

	// Sort by count descending, then alphabetically ascending
	sort.Slice(sorted, func(i, j int) bool {
		if sorted[i].count == sorted[j].count {
			return sorted[i].kmer < sorted[j].kmer
		}
		return sorted[i].count > sorted[j].count
	})

	for _, p := range sorted {
		percentage := float64(p.count) * 100.0 / float64(total)
		fmt.Printf("%s %.3f\n", p.kmer, percentage)
	}
	fmt.Println()
}

// printCount prints the count of a specific k-mer.
func printCount(counts map[string]int, target string) {
	fmt.Printf("%d\t%s\n", counts[target], target)
}

func main() {
	if len(os.Args) < 2 {
		log.Fatalf("Usage: %s <fasta_file>", os.Args[0])
	}
	filename := os.Args[1]

	// The k-nucleotide benchmark specifically targets the third sequence
	seq, err := readSequence(filename, ">THREE")
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	if len(seq) == 0 {
		log.Fatalf("Sequence '>THREE' not found or is empty.")
	}

	// 1-mer and 2-mer frequencies
	printFrequencies(countKmers(seq, 1))
	printFrequencies(countKmers(seq, 2))

	// Specific k-mer counts
	targets := []string{"GGT", "GGTA", "GGTATT", "GGTATTTTAATT", "GGTATTTTAATTTATAGT"}
	for _, target := range targets {
		counts := countKmers(seq, len(target))
		printCount(counts, target)
	}
}
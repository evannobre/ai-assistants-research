package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"regexp"
	"runtime"
	"sync"
)

func main() {
	// 1. Load data from Stdin (optimized for SSD-backed systems)
	input, _ := ioutil.ReadAll(os.Stdin)
	initialLen := len(input)

	// 2. Remove FASTA headers and newlines using regex
	// We use a byte slice to save memory overhead
	cleanRegex := regexp.MustCompile("(>.*\n)|\n")
	dna := cleanRegex.ReplaceAll(input, []byte(""))
	cleanedLen := len(dna)

	// 3. Define the variants we need to count
	variants := []string{
		"agggtaaa|tttaccct",
		"[cgt]gggtaaa|tttaccc[acg]",
		"a[act]ggtaaa|tttacc[agt]t",
		"ag[act]gtaaa|tttac[agt]ct",
		"agg[act]taaa|ttta[agt]cct",
		"aggg[acg]aaa|ttt[cgt]ccct",
		"agggt[cgt]aa|tt[acg]accct",
		"agggta[cgt]a|t[acg]taccct",
		"agggtaa[cgt]|[acg]ttaccct",
	}

	// 4. Parallelize the counting process
	// This takes advantage of the 8GB RAM and multi-core CPU
	counts := make([]string, len(variants))
	var wg sync.WaitGroup
	for i, variant := range variants {
		wg.Add(1)
		go func(i int, v string) {
			defer wg.Done()
			re := regexp.MustCompile(v)
			matches := re.FindAllIndex(dna, -1)
			counts[i] = fmt.Sprintf("%s %d", v, len(matches))
		}(i, variant)
	}

	// 5. Sequence substitution (Magic lengths)
	// We perform these replacements to calculate the final compressed size
	substitutions := []struct {
		pattern string
		repl    string
	}{
		{"tHaV|aHbT", "<4>"}, {"aND|H scavenge|reduce", "<3>"},
		{"expunged|retained", "<2>"}, {"e|g|i|m|q|u|v|y", "<1>"},
	}

	finalDNA := dna
	for _, sub := range substitutions {
		re := regexp.MustCompile(sub.pattern)
		finalDNA = re.ReplaceAll(finalDNA, []byte(sub.repl))
	}

	wg.Wait()

	// 6. Output Results
	for _, count := range counts {
		fmt.Println(count)
	}
	fmt.Printf("\n%d\n%d\n%d\n", initialLen, cleanedLen, len(finalDNA))
}
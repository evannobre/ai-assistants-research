package main

import (
	"bytes"
	"fmt"
	"io"
	"os"
	"regexp"
	"runtime"
	"sync"
)

var patterns = []string{
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

var iubCodes = []struct {
	pattern     string
	replacement string
}{
	{"tHa[Nt]", "<4>"},
	{"aND|caN|Ha[DS]|WaS", "<3>"},
	{"a[NSt]|BY", "<2>"},
	{"<[^>]*>", "|"},
	{"\\|[^|][^|]*\\|", "-"},
}

func main() {
	// Read all input
	input, _ := io.ReadAll(os.Stdin)
	initialLen := len(input)

	// Remove FASTA descriptions and newlines
	sequence := regexp.MustCompile(`>.*\n|\n`).ReplaceAll(input, nil)
	cleanedLen := len(sequence)

	// Count patterns in parallel
	var wg sync.WaitGroup
	results := make([]string, len(patterns))
	
	for i, pattern := range patterns {
		wg.Add(1)
		go func(idx int, pat string) {
			defer wg.Done()
			re := regexp.MustCompile(pat)
			count := len(re.FindAll(sequence, -1))
			results[idx] = fmt.Sprintf("%s %d", pat, count)
		}(i, pattern)
	}
	
	wg.Wait()

	// Print results
	for _, result := range results {
		fmt.Println(result)
	}

	// Perform replacements
	modifiedSeq := sequence
	for _, iub := range iubCodes {
		re := regexp.MustCompile(iub.pattern)
		modifiedSeq = re.ReplaceAll(modifiedSeq, []byte(iub.replacement))
	}

	// Print lengths
	fmt.Println()
	fmt.Println(initialLen)
	fmt.Println(cleanedLen)
	fmt.Println(len(modifiedSeq))
}
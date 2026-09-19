package main

import (
	"fmt"
	"io"
	"os"
	"regexp"
	"sync"
)

func main() {
	// 1. Ingest & Measure
	// Read standard input entirely into a byte slice.
	bytes, err := io.ReadAll(os.Stdin)
	if err != nil {
		panic(err)
	}
	originalLen := len(bytes)

	// 2. Sanitize
	// Remove FASTA descriptions and all linefeeds.
	reClean := regexp.MustCompile(`>.*\n|\n`)
	cleanedText := reClean.ReplaceAll(bytes, []byte{})
	cleanedLen := len(cleanedText)

	// The 9 DNA variants we need to count
	variants := []string{
		`agggtaaa|tttaccct`,
		`[cgt]gggtaaa|tttaccc[acg]`,
		`a[act]ggtaaa|tttacc[agt]t`,
		`ag[act]gtaaa|tttac[agt]ct`,
		`agg[act]taaa|ttta[agt]cct`,
		`aggg[acg]aaa|ttt[cgt]ccct`,
		`agggt[cgt]aa|tt[acg]accct`,
		`agggta[cgt]a|t[acg]taccct`,
		`agggtaa[cgt]|[acg]ttaccct`,
	}

	counts := make([]int, len(variants))
	var wg sync.WaitGroup

	// 3. Fork Execution - Path A (Concurrent Counting)
	for i, variant := range variants {
		wg.Add(1)
		go func(index int, v string) {
			defer wg.Done()
			re := regexp.MustCompile(v)
			// FindAllIndex returns a slice of all successive matches
			matches := re.FindAllIndex(cleanedText, -1)
			counts[index] = len(matches)
		}(i, variant)
	}

	// The 5 sequential "magic" replacements
	replacements := []struct {
		pattern     string
		replacement string
	}{
		{`tHa[Nt]`, `<4>`},
		{`aND|caN|Ha[DS]|WaS`, `<3>`},
		{`a[NSt]|BY`, `<2>`},
		{`<[^>]*>`, `|`},
		{`\|[^|][^|]*\|`, `-`},
	}

	// 3. Fork Execution - Path B (Sequential Replacements)
	// This runs on the main thread concurrently with the counting goroutines.
	finalText := cleanedText
	for _, r := range replacements {
		re := regexp.MustCompile(r.pattern)
		finalText = re.ReplaceAll(finalText, []byte(r.replacement))
	}
	finalLen := len(finalText)

	// Synchronize: block until all 9 counting goroutines report completion
	wg.Wait()

	// 4. Output formatting
	for i, variant := range variants {
		fmt.Printf("%s %d\n", variant, counts[i])
	}
	fmt.Printf("\n%d\n%d\n%d\n", originalLen, cleanedLen, finalLen)
}
package main

import (
	"fmt"
	"io"
	"os"
	"regexp"
)

func main() {
	// Read all input from stdin
	inputData, err := io.ReadAll(os.Stdin)
	if err != nil {
		panic(err)
	}
	
	inputStr := string(inputData)
	initialLength := len(inputStr)
	
	// Remove FASTA descriptions and linefeeds
	re := regexp.MustCompile(`>.*\n|\n`)
	sequence := re.ReplaceAllString(inputStr, "")
	cleanedLength := len(sequence)
	
	// Define the 8-mer patterns
	patterns := []string{
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
	
	// Count matches for each pattern
	for _, pattern := range patterns {
		re := regexp.MustCompile(pattern)
		matches := re.FindAllString(sequence, -1)
		count := len(matches)
		fmt.Printf("%s %d\n", pattern, count)
	}
	
	// Define magic patterns and replacements
	replacements := []struct {
		pattern     string
		replacement string
	}{
		{`tHa[Nt]`, "<4>"},
		{`aND|caN|Ha[DS]|WaS`, "<3>"},
		{`a[NSt]|BY`, "<2>"},
		{`<[^>]*>`, "|"},
		{`\|[^|][^|]*\|`, "-"},
	}
	
	// Apply replacements one at a time
	resultSequence := sequence
	for _, r := range replacements {
		re := regexp.MustCompile(r.pattern)
		resultSequence = re.ReplaceAllString(resultSequence, r.replacement)
	}
	
	finalLength := len(resultSequence)
	
	// Write the three recorded sequence lengths
	fmt.Println()
	fmt.Println(initialLength)
	fmt.Println(cleanedLength)
	fmt.Println(finalLength)
}
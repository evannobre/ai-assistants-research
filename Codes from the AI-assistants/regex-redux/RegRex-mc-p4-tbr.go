// regex_redux.go
package main

import (
    "bufio"
    "bytes"
    "fmt"
    "io"
    "os"
    "regexp"
)

func main() {
    // Read all stdin
    data, err := io.ReadAll(bufio.NewReader(os.Stdin))
    if err != nil {
        fmt.Fprintln(os.Stderr, "read error:", err)
        os.Exit(1)
    }
    // L1: original length
    L1 := len(data)

    // Step 2: remove FASTA descriptions and newlines
    // Pattern: (?m)^>.*\n|\n
    // Use MustCompile once
    removeHeaderNewline := regexp.MustCompile(`(?m)^>.*\n|\n`)
    cleaned := removeHeaderNewline.ReplaceAll(data, []byte{})
    L2 := len(cleaned)

    // Convert cleaned to string for regex operations
    seq := string(cleaned)

    // Step 3: DNA 8-mer patterns (case-insensitive)
    patterns := []string{
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

    // For each pattern, compile with case-insensitive flag (?i) and count matches
    for _, p := range patterns {
        re := regexp.MustCompile("(?i)" + p)
        matches := re.FindAllStringIndex(seq, -1)
        fmt.Printf("%s %d\n", p, len(matches))
    }

    // Step 4: magic patterns and replacements (applied sequentially)
    // Patterns and replacements in order
    magicPatterns := []string{
        "tHa[Nt]",
        "aND|caN|Ha[DS]|WaS",
        "a[NSt]|BY",
        "<[^>]*>",
        `\\|[^|][^|]*\\|`,
    }
    replacements := []string{
        "<4>",
        "<3>",
        "<2>",
        "|",
        "-",
    }

    // Apply each replacement sequentially
    working := seq
    for i, mp := range magicPatterns {
        // For textual patterns that are intended to be case-insensitive in the original benchmark,
        // use (?i) to match both cases. The original regex-redux uses case-sensitive for angle-bracket and pipe patterns,
        // but textual patterns like tHa[Nt] and aND|... are matched case-insensitively in many reference implementations.
        // To preserve behavior, apply (?i) for the first three patterns, and no (?i) for the last two.
        var re *regexp.Regexp
        if i <= 2 {
            re = regexp.MustCompile("(?i)" + mp)
        } else {
            re = regexp.MustCompile(mp)
        }
        working = re.ReplaceAllString(working, replacements[i])
    }

    L3 := len(working)

    // Step 5: print lengths
    fmt.Printf("\n%d\n%d\n%d\n", L1, L2, L3)
}

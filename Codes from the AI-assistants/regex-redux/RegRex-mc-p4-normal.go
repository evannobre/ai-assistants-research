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
    // 1. Read all input from stdin
    var buf bytes.Buffer
    if _, err := io.Copy(&buf, os.Stdin); err != nil {
        panic(err)
    }
    data := buf.String()
    lenOriginal := len(data)

    // 2. Remove FASTA headers and newlines using regex
    // Remove description lines starting with '>'
    reHeader := regexp.MustCompile(`(?m)^>.*\n`)
    withoutHeaders := reHeader.ReplaceAllString(data, "")
    // Remove all linefeeds
    reNewline := regexp.MustCompile("\n")
    seq := reNewline.ReplaceAllString(withoutHeaders, "")
    lenCleaned := len(seq)

    // 3. Count occurrences of 8-mer patterns
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

    writer := bufio.NewWriter(os.Stdout)
    defer writer.Flush()

    for _, p := range patterns {
        re := regexp.MustCompile(p)
        // Count matches by iterating over all matches
        matches := re.FindAllStringIndex(seq, -1)
        count := len(matches)
        fmt.Fprintf(writer, "%s %d\n", p, count)
    }

    fmt.Fprintln(writer)

    // 4. Apply magic regex replacements in sequence
    type repl struct {
        pat string
        rep string
    }

    replacements := []repl{
        {`tHa[Nt]`, "<4>"},
        {`aND|caN|Ha[DS]|WaS`, "<3>"},
        {`a[NSt]|BY`, "<2>"},
        {`<[^>]*>`, "|"},
        {`\\|[^|][^|]*\\|`, "-"},
    }

    current := seq
    for _, r := range replacements {
        re := regexp.MustCompile(r.pat)
        current = re.ReplaceAllString(current, r.rep)
    }
    lenFinal := len(current)

    // 5. Print lengths
    fmt.Fprintf(writer, "%d\n", lenOriginal)
    fmt.Fprintf(writer, "%d\n", lenCleaned)
    fmt.Fprintf(writer, "%d\n", lenFinal)
}

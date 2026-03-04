// regex_redux.go
package main

import (
    "bufio"
    "bytes"
    "fmt"
    "io"
    "os"
    "regexp"
    "runtime"
    "sync"
)

func readSequence(r io.Reader) ([]byte, error) {
    br := bufio.NewReaderSize(r, 1<<20) // 1MB buffer
    var buf bytes.Buffer
    for {
        line, err := br.ReadBytes('\n')
        if len(line) > 0 {
            // Skip header lines starting with '>'
            if line[0] == '>' {
                continue
            }
            // Remove newline characters and append
            // Trim trailing \n or \r\n
            if line[len(line)-1] == '\n' {
                line = line[:len(line)-1]
            }
            if len(line) > 0 && line[len(line)-1] == '\r' {
                line = line[:len(line)-1]
            }
            buf.Write(line)
        }
        if err != nil {
            if err == io.EOF {
                break
            }
            return nil, err
        }
    }
    // Return a copy of the buffer bytes to avoid exposing internal buffer
    seq := make([]byte, buf.Len())
    copy(seq, buf.Bytes())
    return seq, nil
}

func countMatches(seq []byte, patterns []*regexp.Regexp) []int {
    n := len(patterns)
    counts := make([]int, n)

    // Use concurrency for counting patterns; safe because regexp is goroutine-safe.
    var wg sync.WaitGroup
    wg.Add(n)
    for i, re := range patterns {
        go func(i int, re *regexp.Regexp) {
            defer wg.Done()
            // FindAllIndex returns [][]int; length is the count
            // Use FindAllIndex on the byte slice
            matches := re.FindAllIndex(seq, -1)
            if matches != nil {
                counts[i] = len(matches)
            } else {
                counts[i] = 0
            }
        }(i, re)
    }
    wg.Wait()
    return counts
}

func applySubstitutions(seq []byte, subs [][2]string) []byte {
    // Apply substitutions sequentially
    current := seq
    for _, s := range subs {
        pat := s[0]
        repl := s[1]
        re := regexp.MustCompile(pat)
        // ReplaceAllString accepts string; convert once
        current = []byte(re.ReplaceAllString(string(current), repl))
    }
    return current
}

func main() {
    // Allow Go to use all CPUs available
    runtime.GOMAXPROCS(runtime.NumCPU())

    // Read sequence from stdin (benchmark usually pipes input)
    seq, err := readSequence(os.Stdin)
    if err != nil {
        fmt.Fprintf(os.Stderr, "error reading input: %v\n", err)
        os.Exit(1)
    }

    // Patterns to count (example set from regex-redux)
    patternStrs := []string{
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

    // Precompile patterns
    patterns := make([]*regexp.Regexp, 0, len(patternStrs))
    for _, p := range patternStrs {
        patterns = append(patterns, regexp.MustCompile(p))
    }

    // Substitutions (pattern -> replacement)
    subs := [][2]string{
        {"tHa[Nt]", "<4>"},
        {"aND|caN|Ha[DS]|WaS", "<3>"},
        {"a[NSt]|BY", "<2>"},
        {"<[^>]*>", "|"},
        {"\\|[^|][^|]*\\|", "-"},
    }

    // Count matches
    counts := countMatches(seq, patterns)

    // Print counts in the same order as patterns
    for i, c := range counts {
        fmt.Printf("%s %d\n", patternStrs[i], c)
    }

    // Print original length
    fmt.Printf("\nOriginal length: %d\n", len(seq))

    // Apply substitutions
    final := applySubstitutions(seq, subs)

    // Print final length
    fmt.Printf("Final length: %d\n", len(final))
}

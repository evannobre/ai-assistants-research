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
    // 1. Read all input
    data, err := io.ReadAll(bufio.NewReader(os.Stdin))
    if err != nil {
        panic(err)
    }
    input := string(data)
    lenOriginal := len(input)

    // 2. Strip headers and newlines
    reHeader := regexp.MustCompile(`>[^\n]*\n`)
    reNewline := regexp.MustCompile(`\n`)

    seq := reHeader.ReplaceAllString(input, "")
    seq = reNewline.ReplaceAllString(seq, "")
    lenCleaned := len(seq)

    // 3. Count 8-mer patterns
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

    var buf bytes.Buffer

    for _, p := range patterns {
        re := regexp.MustCompile(p)
        matches := re.FindAllStringIndex(seq, -1)
        fmt.Fprintf(&buf, "%s %d\n", p, len(matches))
    }

    // 4. Magic substitutions
    type subst struct {
        pat string
        rep string
    }

    subs := []subst{
        {`tHa[Nt]`, `<4>`},
        {`aND|caN|Ha[DS]|WaS`, `<3>`},
        {`a[NSt]|BY`, `<2>`},
        {`<[^>]*>`, `|`},
        {`\\|[^|][^|]*\\|`, `-`},
    }

    s := seq
    for _, sub := range subs {
        re := regexp.MustCompile(sub.pat)
        s = re.ReplaceAllString(s, sub.rep)
    }
    lenFinal := len(s)

    // 5. Output
    // lengths
    fmt.Println(lenOriginal)
    fmt.Println(lenCleaned)
    fmt.Println(lenFinal)

    // pattern counts
    fmt.Print(buf.String())
}

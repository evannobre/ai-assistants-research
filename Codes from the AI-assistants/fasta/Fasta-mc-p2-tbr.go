// fasta.go
// FASTA simulation using a naïve LCG PRNG.
// Uses only Go standard library. Streams output to stdout.
// Build: go build -o fasta fasta.go
// Run example: ./fasta -n 1000000

package main

import (
    "bufio"
    "flag"
    "fmt"
    "os"
    "strings"
)

// LCG constants (classic FASTA benchmark values)
const (
    IM = 139968
    IA = 3877
    IC = 29573
)

// PRNG holds the LCG state.
type PRNG struct {
    seed int
}

// NewPRNG returns a new PRNG seeded with s.
func NewPRNG(s int) *PRNG { return &PRNG{seed: s} }

// Next returns a pseudo-random float64 in [0,1).
func (r *PRNG) Next() float64 {
    r.seed = (r.seed*IA + IC) % IM
    return float64(r.seed) / float64(IM)
}

// writeWrapped writes bytes from s to w with lines of width 'width'.
// It writes directly to the provided bufio.Writer in chunks.
func writeWrapped(w *bufio.Writer, s string, width int) error {
    n := len(s)
    for i := 0; i < n; i += width {
        end := i + width
        if end > n {
            end = n
        }
        if _, err := w.WriteString(s[i:end]); err != nil {
            return err
        }
        if err := w.WriteByte('\n'); err != nil {
            return err
        }
    }
    return nil
}

// makeRepeat outputs the repeated sequence 'alu' up to length 'n'.
func makeRepeat(w *bufio.Writer, alu string, n int, width int) error {
    // Build a buffer of at least width characters to write efficiently.
    aluLen := len(alu)
    if aluLen == 0 {
        return nil
    }
    out := make([]byte, 0, width)
    pos := 0
    for written := 0; written < n; {
        out = out[:0]
        for len(out) < width && written < n {
            out = append(out, alu[pos%aluLen])
            pos++
            written++
        }
        if _, err := w.Write(out); err != nil {
            return err
        }
        if err := w.WriteByte('\n'); err != nil {
            return err
        }
    }
    return nil
}

// makeRandom outputs a random sequence of length n using alphabet and freqs.
func makeRandom(w *bufio.Writer, pr *PRNG, alphabet []byte, freqs []float64, n int, width int) error {
    // Build cumulative probabilities
    m := len(alphabet)
    cum := make([]float64, m)
    sum := 0.0
    for i := 0; i < m; i++ {
        sum += freqs[i]
        cum[i] = sum
    }
    // Normalize to 1.0 in case of rounding
    for i := 0; i < m; i++ {
        cum[i] /= sum
    }

    buf := make([]byte, 0, width)
    for written := 0; written < n; {
        buf = buf[:0]
        for len(buf) < width && written < n {
            r := pr.Next()
            // linear scan (alphabet small)
            for i := 0; i < m; i++ {
                if r < cum[i] {
                    buf = append(buf, alphabet[i])
                    break
                }
            }
            written++
        }
        if _, err := w.Write(buf); err != nil {
            return err
        }
        if err := w.WriteByte('\n'); err != nil {
            return err
        }
    }
    return nil
}

func main() {
    // CLI flags
    n := flag.Int("n", 1000000, "length of random sequence to generate")
    seed := flag.Int("seed", 42, "PRNG seed")
    width := flag.Int("width", 60, "line width for FASTA output")
    flag.Parse()

    // Prepare writer with a large buffer to reduce syscalls
    out := bufio.NewWriterSize(os.Stdout, 64*1024)
    defer out.Flush()

    // Example repeat sequence (alu) from FASTA benchmark
    alu := "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG" +
        "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA" +
        "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT" +
        "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA" +
        "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG" +
        "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC" +
        "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"

    // Header and repeat block
    fmt.Fprintf(out, ">ONE Homo sapiens alu\n")
    if err := makeRepeat(out, alu, 2*(*n), *width); err != nil {
        fmt.Fprintln(os.Stderr, "error writing repeat:", err)
        return
    }

    // Header for random block
    fmt.Fprintf(out, ">TWO Random DNA\n")

    // DNA alphabet and frequencies (example from FASTA)
    alphabet := []byte{'a', 'c', 'g', 't', 'n'}
    freqs := []float64{0.27, 0.12, 0.12, 0.27, 0.22} // example distribution

    pr := NewPRNG(*seed)
    if err := makeRandom(out, pr, alphabet, freqs, *n, *width); err != nil {
        fmt.Fprintln(os.Stderr, "error writing random:", err)
        return
    }
}

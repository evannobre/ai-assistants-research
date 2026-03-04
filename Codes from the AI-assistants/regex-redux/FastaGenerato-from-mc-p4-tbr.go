// gen_fasta.go
package main

import (
    "fmt"
    "math/rand"
    "os"
    "strconv"
    "time"
)

var alu = []byte(
    "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGG" +
    "GAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTTCGAGA" +
    "CCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAAT" +
    "ACAAAAATTAGCCGGGCGTGGTGGCGCGCGCCTGTAATCCCA" +
    "GCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGG" +
    "AGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCC" +
    "AGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA")

func main() {
    if len(os.Args) < 2 {
        fmt.Fprintln(os.Stderr, "usage: gen_fasta <size>")
        os.Exit(1)
    }
    target, err := strconv.Atoi(os.Args[1])
    if err != nil {
        fmt.Fprintln(os.Stderr, "invalid size:", err)
        os.Exit(1)
    }
    rand.Seed(time.Now().UnixNano())

    // Header
    fmt.Println(">ONE Homo sapiens alu")
    out := make([]byte, 0, target+100)
    for len(out) < target {
        // append a random slice of alu
        start := rand.Intn(len(alu))
        end := start + rand.Intn(60) + 1
        for i := start; i < end; i++ {
            out = append(out, alu[i%len(alu)])
            if len(out) >= target {
                break
            }
        }
    }
    // Write with line breaks every 60 chars
    for i := 0; i < len(out); i += 60 {
        end := i + 60
        if end > len(out) {
            end = len(out)
        }
        fmt.Println(string(out[i:end]))
    }
}

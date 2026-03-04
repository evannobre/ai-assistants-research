package main

import (
    "bufio"
    "bytes"
    "fmt"
    "io"
    "os"
)

const lineWidth = 60

func buildComplementTable() [256]byte {
    var comp [256]byte
    for i := 0; i < 256; i++ {
        comp[i] = byte(i)
    }

    // Uppercase
    comp['A'] = 'T'
    comp['C'] = 'G'
    comp['G'] = 'C'
    comp['T'] = 'A'
    comp['U'] = 'A'
    comp['M'] = 'K'
    comp['R'] = 'Y'
    comp['W'] = 'W'
    comp['S'] = 'S'
    comp['Y'] = 'R'
    comp['K'] = 'M'
    comp['V'] = 'B'
    comp['H'] = 'D'
    comp['D'] = 'H'
    comp['B'] = 'V'
    comp['N'] = 'N'

    // Lowercase (optional but nice)
    comp['a'] = 't'
    comp['c'] = 'g'
    comp['g'] = 'c'
    comp['t'] = 'a'
    comp['u'] = 'a'
    comp['m'] = 'k'
    comp['r'] = 'y'
    comp['w'] = 'w'
    comp['s'] = 's'
    comp['y'] = 'r'
    comp['k'] = 'm'
    comp['v'] = 'b'
    comp['h'] = 'd'
    comp['d'] = 'h'
    comp['b'] = 'v'
    comp['n'] = 'n'

    return comp
}

func reverseComplement(seq []byte, comp [256]byte) {
    i, j := 0, len(seq)-1
    for i <= j {
        ci := comp[seq[i]]
        cj := comp[seq[j]]
        if i == j {
            seq[i] = ci
        } else {
            seq[i] = cj
            seq[j] = ci
        }
        i++
        j--
    }
}

func writeWrapped(w *bufio.Writer, seq []byte) error {
    for len(seq) > 0 {
        n := lineWidth
        if len(seq) < n {
            n = len(seq)
        }
        if _, err := w.Write(seq[:n]); err != nil {
            return err
        }
        if err := w.WriteByte('\n'); err != nil {
            return err
        }
        seq = seq[n:]
    }
    return nil
}

func main() {
    comp := buildComplementTable()

    reader := bufio.NewReader(os.Stdin)
    writer := bufio.NewWriter(os.Stdout)
    defer writer.Flush()

    var header []byte
    sequence := make([]byte, 0, 64*1024) // start with 64KB, will grow as needed

    processRecord := func() error {
        if header == nil || len(sequence) == 0 {
            return nil
        }
        // Write header
        if _, err := writer.Write(header); err != nil {
            return err
        }
        if len(header) == 0 || header[len(header)-1] != '\n' {
            if err := writer.WriteByte('\n'); err != nil {
                return err
            }
        }
        // Reverse-complement in-place
        reverseComplement(sequence, comp)
        // Write wrapped sequence
        return writeWrapped(writer, sequence)
    }

    for {
        line, err := reader.ReadBytes('\n')
        if len(line) > 0 {
            // Trim trailing newline and carriage return
            line = bytes.TrimRight(line, "\r\n")

            if len(line) > 0 && line[0] == '>' {
                // New header: process previous record
                if err2 := processRecord(); err2 != nil {
                    fmt.Fprintln(os.Stderr, "error processing record:", err2)
                    os.Exit(1)
                }
                // Store new header
                header = append(header[:0], line...)
                // Reset sequence (reuse capacity)
                sequence = sequence[:0]
            } else if len(line) > 0 {
                // Sequence line: append
                sequence = append(sequence, line...)
            }
        }

        if err == io.EOF {
            break
        }
        if err != nil {
            fmt.Fprintln(os.Stderr, "read error:", err)
            os.Exit(1)
        }
    }

    // Process last record
    if err := processRecord(); err != nil {
        fmt.Fprintln(os.Stderr, "error processing last record:", err)
        os.Exit(1)
    }
}

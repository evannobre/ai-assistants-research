package main

import (
  "bufio"
  "fmt"
  "os"
  "strconv"
)

const (
  IM = 139968
  IA = 3877
  IC = 29573
)

var seed = 42

func genRandom(max float64) float64 {
  seed = (seed*IA + IC) % IM
  return max * float64(seed) / float64(IM)
}

func cumulativeFromMap(pairs [][2]interface{}) ([]float64, []rune) {
  cum := make([]float64, 0, len(pairs))
  chars := make([]rune, 0, len(pairs))
  s := 0.0
  for _, kv := range pairs {
    ch := kv[0].(rune)
    prob := kv[1].(float64)
    s += prob
    cum = append(cum, s)
    chars = append(chars, ch)
  }
  return cum, chars
}

func emitRepeat(w *bufio.Writer, id, desc, src string, n int) {
  fmt.Fprintf(w, ">%s %s\n", id, desc)
  l := len(src)
  i := 0
  line := make([]rune, 0, 60)
  for produced := 0; produced < n; produced++ {
    line = append(line, rune(src[i%l]))
    i++
    if len(line) == 60 {
      w.WriteString(string(line) + "\n")
      line = line[:0]
    }
  }
  if len(line) > 0 {
    w.WriteString(string(line) + "\n")
  }
}

func emitRandom(w *bufio.Writer, id, desc string, cum []float64, chars []rune, n int) {
  fmt.Fprintf(w, ">%s %s\n", id, desc)
  line := make([]rune, 0, 60)
  for i := 0; i < n; i++ {
    r := genRandom(1.0)
    // linear search
    for j, p := range cum {
      if p > r {
        line = append(line, chars[j])
        break
      }
    }
    if len(line) == 60 {
      w.WriteString(string(line) + "\n")
      line = line[:0]
    }
  }
  if len(line) > 0 {
    w.WriteString(string(line) + "\n")
  }
}

func main() {
  N := 25000000
  if len(os.Args) > 1 {
    if v, err := strconv.Atoi(os.Args[1]); err == nil {
      N = v
    }
  }
  w := bufio.NewWriterSize(os.Stdout, 1<<20)
  defer w.Flush()

  alu := "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGATCACCTGAGGT" +
    "CAGGAGTTCGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAATACAAAAATTAGCC" +
    "GGGCGTGGTGGCGCGCGCCTGTAATCCCAGCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCC" +
    "GGGAGGCGGAGGTTGCAGTGAGCCGAGATCGCGCCACTGCACTCCAGCCTGGGCGACAGAGCGAGACT" +
    "CCGTCTCAAAAA"

  iub := [][2]interface{}{
    {'a', 0.27}, {'c', 0.12}, {'g', 0.12}, {'t', 0.27},
    {'B', 0.02}, {'D', 0.02}, {'H', 0.02}, {'K', 0.02},
    {'M', 0.02}, {'N', 0.02}, {'R', 0.02}, {'S', 0.02},
    {'V', 0.02}, {'W', 0.02}, {'Y', 0.02},
  }
  hs := [][2]interface{}{
    {'a', 0.3029549426680}, {'c', 0.1979883004921},
    {'g', 0.1975473066391}, {'t', 0.3015094502008},
  }

  cumIub, charsIub := cumulativeFromMap(iub[:])
  cumHs, charsHs := cumulativeFromMap(hs[:])

  emitRepeat(w, "ONE", "Homo sapiens alu", alu, 2*N)
  emitRandom(w, "TWO", "IUB ambiguity codes", cumIub, charsIub, 3*N)
  emitRandom(w, "THREE", "Homo sapiens frequency", cumHs, charsHs, 5*N)
}

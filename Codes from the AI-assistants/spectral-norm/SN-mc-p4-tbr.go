package main

import (
    "fmt"
    "math"
    "os"
    "runtime"
    "strconv"
    "sync"
)

// A returns the (i,j) element of the infinite matrix as described.
// i and j are 1-based indices.
func A(i, j int) float64 {
    d := i + j - 1
    n := (d-1)*d/2 + j
    return 1.0 / float64(n)
}

// mulA computes y = A * x for an n-length vector x.
// Returns a newly allocated slice of length n.
func mulA(x []float64) []float64 {
    n := len(x)
    y := make([]float64, n)
    // Parallelize by splitting rows among workers
    workers := runtime.GOMAXPROCS(0)
    var wg sync.WaitGroup
    chunk := (n + workers - 1) / workers
    for w := 0; w < workers; w++ {
        start := w * chunk
        end := start + chunk
        if end > n {
            end = n
        }
        if start >= end {
            continue
        }
        wg.Add(1)
        go func(s, e int) {
            defer wg.Done()
            for i := s; i < e; i++ {
                var sum float64
                ii := i + 1 // convert to 1-based
                for j := 1; j <= n; j++ {
                    sum += A(ii, j) * x[j-1]
                }
                y[i] = sum
            }
        }(start, end)
    }
    wg.Wait()
    return y
}

// mulAt computes y = A^T * x for an n-length vector x.
// Returns a newly allocated slice of length n.
func mulAt(x []float64) []float64 {
    n := len(x)
    y := make([]float64, n)
    workers := runtime.GOMAXPROCS(0)
    var wg sync.WaitGroup
    chunk := (n + workers - 1) / workers
    for w := 0; w < workers; w++ {
        start := w * chunk
        end := start + chunk
        if end > n {
            end = n
        }
        if start >= end {
            continue
        }
        wg.Add(1)
        go func(s, e int) {
            defer wg.Done()
            for j := s; j < e; j++ {
                var sum float64
                jj := j + 1 // 1-based
                for i := 1; i <= n; i++ {
                    sum += A(i, jj) * x[i-1]
                }
                y[j] = sum
            }
        }(start, end)
    }
    wg.Wait()
    return y
}

// mulAtA computes y = A^T * (A * x) without forming A explicitly.
func mulAtA(x []float64) []float64 {
    // first compute tmp = A * x
    tmp := mulA(x)
    // then compute y = A^T * tmp
    return mulAt(tmp)
}

// dot computes the dot product of two vectors of equal length.
func dot(a, b []float64) float64 {
    var sum float64
    n := len(a)
    for i := 0; i < n; i++ {
        sum += a[i] * b[i]
    }
    return sum
}

func main() {
    // default n
    n := 5500
    if len(os.Args) > 1 {
        if v, err := strconv.Atoi(os.Args[1]); err == nil && v > 0 {
            n = v
        }
    }

    // Set GOMAXPROCS to available CPUs for best throughput
    runtime.GOMAXPROCS(runtime.NumCPU())

    // initialize u to all ones
    u := make([]float64, n)
    for i := 0; i < n; i++ {
        u[i] = 1.0
    }
    var v []float64

    // perform 10 iterations of the power method on A^T A
    // (this is the standard approach used in the spectral-norm benchmark)
    for iter := 0; iter < 10; iter++ {
        v = mulAtA(u)
        u = mulAtA(v)
    }

    // compute Rayleigh quotient sqrt((u·v)/(v·v))
    numer := dot(u, v)
    denom := dot(v, v)
    result := math.Sqrt(numer / denom)

    // print with 9 decimal places
    fmt.Printf("%.9f\n", result)
}

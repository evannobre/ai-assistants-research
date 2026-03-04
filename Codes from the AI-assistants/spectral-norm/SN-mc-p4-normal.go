package main

import (
    "fmt"
    "math"
    "os"
    "strconv"
)

// (i) A(i, j): infinite matrix element, 0-based indices
func A(i, j int) float64 {
    ij := i + j
    return 1.0 / (float64(ij*(ij+1)/2 + i + 1))
}

// (ii) Av: y = A * v
func Av(n int, v, y []float64) {
    for i := 0; i < n; i++ {
        sum := 0.0
        for j := 0; j < n; j++ {
            sum += A(i, j) * v[j]
        }
        y[i] = sum
    }
}

// (iii) Atv: y = A^T * v
func Atv(n int, v, y []float64) {
    for i := 0; i < n; i++ {
        sum := 0.0
        for j := 0; j < n; j++ {
            sum += A(j, i) * v[j]
        }
        y[i] = sum
    }
}

// (iv) AtAv: y = A^T * (A * v)
func AtAv(n int, v, y []float64) {
    tmp := make([]float64, n)
    Av(n, v, tmp)
    Atv(n, tmp, y)
}

func main() {
    // Default size if no argument is given
    n := 5500
    if len(os.Args) > 1 {
        if val, err := strconv.Atoi(os.Args[1]); err == nil && val > 0 {
            n = val
        }
    }

    u := make([]float64, n)
    v := make([]float64, n)

    // Initialize u with 1s
    for i := range u {
        u[i] = 1.0
    }

    // Power method iterations
    for iter := 0; iter < 10; iter++ {
        AtAv(n, u, v)
        AtAv(n, v, u)
    }

    // Compute Rayleigh quotient approximation
    vBv := 0.0
    vv := 0.0
    for i := 0; i < n; i++ {
        vBv += u[i] * v[i]
        vv += v[i] * v[i]
    }

    spectralNorm := math.Sqrt(vBv / vv)
    fmt.Printf("%.9f\n", spectralNorm)
}

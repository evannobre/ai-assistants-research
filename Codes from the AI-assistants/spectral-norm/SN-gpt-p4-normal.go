package main

import (
	"fmt"
	"math"
	"os"
	"runtime"
	"strconv"
	"sync"
)

// A(i,j) for the matrix described by:
// a11=1, a12=1/2, a21=1/3, a13=1/4, a22=1/5, a31=1/6, ...
//
// Using 0-based indices i,j:
// A(i,j) = 1 / ( t + i + 1 ), where t = (i+j)(i+j+1)/2
func A(i, j int) float64 {
	ij := i + j
	t := ij * (ij + 1) / 2
	return 1.0 / float64(t+i+1)
}

// Computes out = A * v
func Av(v, out []float64) {
	n := len(v)
	for i := 0; i < n; i++ {
		sum := 0.0
		for j := 0; j < n; j++ {
			sum += A(i, j) * v[j]
		}
		out[i] = sum
	}
}

// Computes out = A^T * v
func Atv(v, out []float64) {
	n := len(v)
	for i := 0; i < n; i++ {
		sum := 0.0
		for j := 0; j < n; j++ {
			sum += A(j, i) * v[j]
		}
		out[i] = sum
	}
}

// Computes out = A^T * (A * v) using tmp as scratch: tmp = A*v
func AtAv(v, out, tmp []float64) {
	Av(v, tmp)
	Atv(tmp, out)
}

// Dot product
func dot(a, b []float64) float64 {
	sum := 0.0
	for i := range a {
		sum += a[i] * b[i]
	}
	return sum
}

// Optional: parallel versions of Av/Atv for better throughput on multi-core CPUs.
// (Still only uses native stdlib.)
func AvParallel(v, out []float64) {
	n := len(v)
	workers := runtime.GOMAXPROCS(0)
	chunk := (n + workers - 1) / workers

	var wg sync.WaitGroup
	wg.Add(workers)
	for w := 0; w < workers; w++ {
		start := w * chunk
		end := start + chunk
		if end > n {
			end = n
		}
		go func(s, e int) {
			defer wg.Done()
			for i := s; i < e; i++ {
				sum := 0.0
				for j := 0; j < n; j++ {
					sum += A(i, j) * v[j]
				}
				out[i] = sum
			}
		}(start, end)
	}
	wg.Wait()
}

func AtvParallel(v, out []float64) {
	n := len(v)
	workers := runtime.GOMAXPROCS(0)
	chunk := (n + workers - 1) / workers

	var wg sync.WaitGroup
	wg.Add(workers)
	for w := 0; w < workers; w++ {
		start := w * chunk
		end := start + chunk
		if end > n {
			end = n
		}
		go func(s, e int) {
			defer wg.Done()
			for i := s; i < e; i++ {
				sum := 0.0
				for j := 0; j < n; j++ {
					sum += A(j, i) * v[j]
				}
				out[i] = sum
			}
		}(start, end)
	}
	wg.Wait()
}

func AtAvParallel(v, out, tmp []float64) {
	AvParallel(v, tmp)
	AtvParallel(tmp, out)
}

func main() {
	// Usage: go run main.go 5500
	n := 5500
	if len(os.Args) > 1 {
		val, err := strconv.Atoi(os.Args[1])
		if err == nil && val > 0 {
			n = val
		}
	}

	// Allocate O(n) memory. No matrix allocation.
	u := make([]float64, n)
	v := make([]float64, n)
	tmp := make([]float64, n)

	for i := 0; i < n; i++ {
		u[i] = 1.0
	}

	// Power method on A^T A (10 iterations is the common benchmark setting).
	// For speed, use parallel AtAv on multi-core machines:
	//   AtAvParallel(...)
	// Otherwise, AtAv(...) is simpler and deterministic.
	for iter := 0; iter < 10; iter++ {
		AtAvParallel(u, v, tmp)
		AtAvParallel(v, u, tmp)
	}

	// Spectral norm estimate
	vBv := dot(u, v)
	vv := dot(v, v)
	result := math.Sqrt(vBv / vv)

	fmt.Printf("%.9f\n", result)
}

package main

import (
	"flag"
	"fmt"
	"math"
	"runtime"
	"sync"
)

// evalA computes the matrix element A[i,j] on the fly.
// We use 0-based indexing, mapping directly to your specified sequence.
func evalA(i, j int) float64 {
	fi, fj := float64(i), float64(j)
	return 1.0 / (((fi+fj)*(fi+fj+1))/2.0 + fi + 1.0)
}

// evalATimesU computes v = A * u concurrently
func evalATimesU(u, v []float64, workers int) {
	var wg sync.WaitGroup
	n := len(u)
	chunk := (n + workers - 1) / workers

	for w := 0; w < workers; w++ {
		start := w * chunk
		end := start + chunk
		if end > n {
			end = n
		}
		if start >= n {
			break
		}

		wg.Add(1)
		go func(start, end int) {
			defer wg.Done()
			for i := start; i < end; i++ {
				var sum float64
				for j := 0; j < n; j++ {
					sum += evalA(i, j) * u[j]
				}
				v[i] = sum
			}
		}(start, end)
	}
	wg.Wait()
}

// evalAtTimesU computes v = A^T * u concurrently
func evalAtTimesU(u, v []float64, workers int) {
	var wg sync.WaitGroup
	n := len(u)
	chunk := (n + workers - 1) / workers

	for w := 0; w < workers; w++ {
		start := w * chunk
		end := start + chunk
		if end > n {
			end = n
		}
		if start >= n {
			break
		}

		wg.Add(1)
		go func(start, end int) {
			defer wg.Done()
			for i := start; i < end; i++ {
				var sum float64
				for j := 0; j < n; j++ {
					// Swap i and j to transpose the matrix
					sum += evalA(j, i) * u[j]
				}
				v[i] = sum
			}
		}(start, end)
	}
	wg.Wait()
}

// evalAtATimesU computes v = A^T * A * u
func evalAtATimesU(u, v, tmp []float64, workers int) {
	evalATimesU(u, tmp, workers)
	evalAtTimesU(tmp, v, workers)
}

func main() {
	// N determines the precision of the infinite matrix approximation.
	// N=5500 is the industry standard for this benchmark.
	nPtr := flag.Int("n", 5500, "Size of the N x N matrix")
	flag.Parse()
	N := *nPtr

	// Optimize thread count based on your specific Ubuntu hardware
	workers := runtime.NumCPU()

	// Allocate O(N) memory. For N=5500, this is ~132 KB total.
	u := make([]float64, N)
	v := make([]float64, N)
	tmp := make([]float64, N)

	// Initialize vector u with 1.0s
	for i := 0; i < N; i++ {
		u[i] = 1.0
	}

	// Apply the Power Method. 10 iterations guarantee 9 decimal places of precision
	// for this specific matrix structure.
	for i := 0; i < 10; i++ {
		evalAtATimesU(u, v, tmp, workers)
		evalAtATimesU(v, u, tmp, workers)
	}

	// Compute the Rayleigh quotient: (u^T * v) / (v^T * v)
	var vBv, vv float64
	for i := 0; i < N; i++ {
		vBv += u[i] * v[i]
		vv += v[i] * v[i]
	}

	// The spectral norm is the square root of the largest eigenvalue of A^T * A
	spectralNorm := math.Sqrt(vBv / vv)

	fmt.Printf("%0.9f\n", spectralNorm)
}
package main

import (
	"flag"
	"fmt"
	"math"
	"runtime"
	"sync"
)

// evalA calculates the matrix entry A_{i,j} based on the Cantor pairing function.
func evalA(i, j int) float64 {
	return 1.0 / float64(((i+j)*(i+j+1))/2+i+1)
}

// multiplyAu multiplies matrix A by vector u, storing the result in v.
// It chunks the work across available CPU cores for concurrency.
func multiplyAu(u, v []float64, workers int) {
	n := len(u)
	var wg sync.WaitGroup
	chunkSize := (n + workers - 1) / workers

	for w := 0; w < workers; w++ {
		start := w * chunkSize
		end := start + chunkSize
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

// multiplyAtu multiplies the transpose of matrix A by vector u, storing the result in v.
func multiplyAtu(u, v []float64, workers int) {
	n := len(u)
	var wg sync.WaitGroup
	chunkSize := (n + workers - 1) / workers

	for w := 0; w < workers; w++ {
		start := w * chunkSize
		end := start + chunkSize
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
					sum += evalA(j, i) * u[j] // Note the j, i reversal for transpose
				}
				v[i] = sum
			}
		}(start, end)
	}
	wg.Wait()
}

// multiplyAtAu performs v = A^T * A * u
func multiplyAtAu(u, v, tmp []float64, workers int) {
	multiplyAu(u, tmp, workers)
	multiplyAtu(tmp, v, workers)
}

func main() {
	n := flag.Int("n", 5500, "Size of the simulated infinite matrix")
	flag.Parse()

	// Hardware concurrency mapping
	workers := runtime.NumCPU()

	u := make([]float64, *n)
	v := make([]float64, *n)
	tmp := make([]float64, *n)

	// Initialize vector u with 1s
	for i := 0; i < *n; i++ {
		u[i] = 1.0
	}

	// Power Method: 10 iterations of v = A^T * A * u
	for i := 0; i < 10; i++ {
		multiplyAtAu(u, v, tmp, workers)
		multiplyAtAu(v, u, tmp, workers)
	}

	// Calculate the Rayleigh quotient to approximate the spectral norm
	var vBv, vv float64
	for i := 0; i < *n; i++ {
		vBv += u[i] * v[i]
		vv += v[i] * v[i]
	}

	spectralNorm := math.Sqrt(vBv / vv)
	fmt.Printf("%0.9f\n", spectralNorm)
}
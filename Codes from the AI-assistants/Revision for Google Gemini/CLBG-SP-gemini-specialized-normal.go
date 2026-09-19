package main

import (
	"flag"
	"fmt"
	"math"
	"runtime"
	"strconv"
	"sync"
)

// (i) Computes the infinite matrix element A(i, j)
func evalA(i, j int) float64 {
	return 1.0 / float64(((i+j)*(i+j+1)/2 + i + 1))
}

// (ii) Computes A * u
func evalATimesU(u, v []float64) {
	n := len(u)
	var wg sync.WaitGroup
	workers := runtime.NumCPU()
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
		// Process matrix chunk concurrently
		go func(start, end int) {
			defer wg.Done()
			for i := start; i < end; i++ {
				sum := 0.0
				for j := 0; j < n; j++ {
					sum += evalA(i, j) * u[j]
				}
				v[i] = sum
			}
		}(start, end)
	}
	wg.Wait()
}

// (iii) Computes Aᵗ * u
func evalAtTimesU(u, v []float64) {
	n := len(u)
	var wg sync.WaitGroup
	workers := runtime.NumCPU()
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
		// Process transposed matrix chunk concurrently
		go func(start, end int) {
			defer wg.Done()
			for i := start; i < end; i++ {
				sum := 0.0
				for j := 0; j < n; j++ {
					// Notice j and i are swapped to simulate the Transpose
					sum += evalA(j, i) * u[j]
				}
				v[i] = sum
			}
		}(start, end)
	}
	wg.Wait()
}

// (iv) Computes Aᵗ * (A * u)
func evalAtATimesU(u, v, tmp []float64) {
	evalATimesU(u, tmp)
	evalAtTimesU(tmp, v)
}

func main() {
	// Parse command-line arguments to allow N overrides
	flag.Parse()
	n := 5500
	if flag.NArg() > 0 {
		if parsedN, err := strconv.Atoi(flag.Arg(0)); err == nil {
			n = parsedN
		}
	}

	// Pre-allocate strictly sized vectors
	u := make([]float64, n)
	v := make([]float64, n)
	tmp := make([]float64, n)

	// Initialize vector u to 1
	for i := range u {
		u[i] = 1.0
	}

	// Execute 10 iterations of the Power Method
	for i := 0; i < 10; i++ {
		evalAtATimesU(u, v, tmp)
		evalAtATimesU(v, u, tmp)
	}

	// Calculate the Rayleigh quotient: (vᵗ * u) / (vᵗ * v)
	vBv, vv := 0.0, 0.0
	for i := 0; i < n; i++ {
		vBv += u[i] * v[i]
		vv += v[i] * v[i]
	}

	// Output the approximated spectral norm
	fmt.Printf("%0.9f\n", math.Sqrt(vBv/vv))
}
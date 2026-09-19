package main

import (
	"fmt"
	"math"
	"os"
	"runtime"
	"strconv"
	"sync"
)

// (i) Computes the infinite matrix element A(i, j)
// We use a 0-based index which algebraically translates to the 1-based matrix requested.
func evalA(i, j int) float64 {
	return 1.0 / float64(((i+j)*(i+j+1)/2 + i + 1))
}

// (ii) Computes A * v
// We parallelize the outer loop to distribute the load across multiple CPU cores.
func evalTimesU(u, v []float64) {
	n := len(u)
	var wg sync.WaitGroup
	numCPU := runtime.NumCPU()
	chunkSize := (n + numCPU - 1) / numCPU

	for i := 0; i < numCPU; i++ {
		start := i * chunkSize
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
			for row := start; row < end; row++ {
				var sum float64
				for col := 0; col < n; col++ {
					sum += evalA(row, col) * u[col]
				}
				v[row] = sum
			}
		}(start, end)
	}
	wg.Wait()
}

// (iii) Computes Aᵗ * v
// Similar to evalTimesU, but we transpose the matrix arguments (col, row).
func evalAtTimesU(u, v []float64) {
	n := len(u)
	var wg sync.WaitGroup
	numCPU := runtime.NumCPU()
	chunkSize := (n + numCPU - 1) / numCPU

	for i := 0; i < numCPU; i++ {
		start := i * chunkSize
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
			for row := start; row < end; row++ {
				var sum float64
				for col := 0; col < n; col++ {
					// Notice evalA receives (col, row) to represent the transposed matrix
					sum += evalA(col, row) * u[col]
				}
				v[row] = sum
			}
		}(start, end)
	}
	wg.Wait()
}

// (iv) Computes Aᵗ * (A * v)
// Accepts a pre-allocated 'tmp' slice to prevent allocating memory inside the benchmark loop.
func evalAtATimesU(u, v, tmp []float64) {
	evalTimesU(u, tmp)
	evalAtTimesU(tmp, v)
}

func main() {
	n := 5500 // Default value
	
	// Read larger matrix size from command-line arguments if provided
	if len(os.Args) > 1 {
		if val, err := strconv.Atoi(os.Args[1]); err == nil {
			n = val
		}
	}

	// Memory allocation (O(N)): allocating 3 slices of 5500 float64s. 
	// At ~44KB each, this is completely negligible for your 8GB RAM.
	u := make([]float64, n)
	v := make([]float64, n)
	tmp := make([]float64, n)

	// Initialize the u vector with 1s
	for i := 0; i < n; i++ {
		u[i] = 1.0
	}

	// Power Method: 10 iterations to approximate the dominant eigenvalue
	for i := 0; i < 10; i++ {
		evalAtATimesU(u, v, tmp)
		evalAtATimesU(v, u, tmp)
	}

	// Calculate the Rayleigh quotient to obtain the spectral norm
	var vBv, vv float64
	for i := 0; i < n; i++ {
		vBv += u[i] * v[i]
		vv += v[i] * v[i]
	}

	// Print the result formatted to 9 decimal places
	fmt.Printf("%0.9f\n", math.Sqrt(vBv/vv))
}
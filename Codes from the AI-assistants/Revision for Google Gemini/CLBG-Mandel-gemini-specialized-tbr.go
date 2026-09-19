package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"sync"
)

const (
	// Limit represents the divergence threshold (|z|^2 > 4.0)
	Limit = 4.0 
	// Iterations defines the maximum depth to check for convergence
	Iterations = 50 
)

func main() {
	// 1. Parse command line arguments
	N := 16000 // Default size
	if len(os.Args) > 1 {
		if val, err := strconv.Atoi(os.Args[1]); err == nil && val > 0 {
			N = val
		}
	}

	// 2. Precompute the real and imaginary coordinates linearly
	// Mapping X to [-1.5, 0.5] and Y to [-1.0, 1.0]
	realCoords := make([]float64, N)
	imagCoords := make([]float64, N)
	for i := 0; i < N; i++ {
		realCoords[i] = 2.0*float64(i)/float64(N) - 1.5
		imagCoords[i] = 2.0*float64(i)/float64(N) - 1.0
	}

	// 3. Allocate exact memory for the PBM bitmap
	bytesPerRow := (N + 7) / 8
	bitmap := make([]byte, N*bytesPerRow)

	// 4. Concurrently calculate rows
	var wg sync.WaitGroup
	wg.Add(N)

	for y := 0; y < N; y++ {
		// Spawn a goroutine for each row
		go func(y int) {
			defer wg.Done()
			ci := imagCoords[y]
			rowOffset := y * bytesPerRow

			for x := 0; x < bytesPerRow; x++ {
				var b byte
				
				// Pack 8 pixels into a single byte
				for p := 0; p < 8; p++ {
					pixelX := x*8 + p
					if pixelX >= N {
						break
					}
					
					cr := realCoords[pixelX]
					zr, zi, tr, ti := 0.0, 0.0, 0.0, 0.0

					// Iterate: z_{n+1} = z_n^2 + C
					for i := 0; i < Iterations && tr+ti <= Limit; i++ {
						zi = 2.0*zr*zi + ci
						zr = tr - ti + cr
						tr = zr * zr
						ti = zi * zi
					}

					b <<= 1
					// If it didn't diverge, the point belongs to the set (black pixel)
					if tr+ti <= Limit {
						b |= 1 
					}
				}
				
				// Pad the final byte if N is not a multiple of 8
				if x == bytesPerRow-1 && N%8 != 0 {
					b <<= (8 - N%8)
				}
				bitmap[rowOffset+x] = b
			}
		}(y)
	}

	// Wait for all row computations to finish
	wg.Wait()

	// 5. Write output byte-by-byte via a buffered writer for fast I/O
	out := bufio.NewWriter(os.Stdout)
	defer out.Flush()

	// Write P4 header
	fmt.Fprintf(out, "P4\n%d %d\n", N, N)
	
	// Write binary payload
	out.Write(bitmap)
}
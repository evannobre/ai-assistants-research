package main

import (
	"fmt"
	"math/cmplx"
	"os"
	"strconv"
)

const maxIter = 50

func mandelbrot(c complex128) bool {
	z := complex(0, 0)
	for i := 0; i < maxIter; i++ {
		z = z*z + c
		if cmplx.Abs(z) > 2 {
			return false
		}
	}
	return true
}

func main() {
	if len(os.Args) != 2 {
		fmt.Println("Usage: mandelbrot <size>")
		os.Exit(1)
	}

	N, err := strconv.Atoi(os.Args[1])
	if err != nil || N <= 0 {
		fmt.Println("Invalid size")
		os.Exit(1)
	}

	// Write PBM header
	fmt.Printf("P4\n%d %d\n", N, N)

	// Bitmap row buffer
	row := make([]byte, (N+7)/8)

	for y := 0; y < N; y++ {
		for x := 0; x < N; x++ {
			// Map pixel to complex plane
			real := -1.5 + 2.0*float64(x)/float64(N)
			imag := -1.0 + 2.0*float64(y)/float64(N)
			c := complex(real, imag)

			if mandelbrot(c) {
				row[x/8] |= 1 << uint(7-x%8)
			}
		}
		os.Stdout.Write(row)
		for i := range row {
			row[i] = 0
		}
	}
}
package main

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

func fannkuchRedux(n int) (int, int) {
	// Pre-allocate arrays to keep memory footprint under a few kilobytes
	// and prevent any runtime garbage collection overhead.
	perm := make([]int, n)
	perm1 := make([]int, n)
	count := make([]int, n)

	// Initialize perm1 to [0, 1, 2, ..., n-1]
	for i := 0; i < n; i++ {
		perm1[i] = i
	}

	maxFlipsCount := 0
	checksum := 0
	sign := 1 // Used to toggle +/- for the checksum

	for {
		// 1. Copy the current permutation to the working array
		for i := 0; i < n; i++ {
			perm[i] = perm1[i]
		}

		first := perm[0]
		flipsCount := 0

		// 2. Count flips if the first element is not already in the 0th position
		if first != 0 {
			for {
				flipsCount++

				// Reverse the first `first + 1` elements.
				// Since we swap the outer bounds (perm[0] and perm[first]) explicitly,
				// we only iterate the inner bounds: from index 1 up to first - 1.
				for i, j := 1, first-1; i < j; i, j = i+1, j-1 {
					perm[i], perm[j] = perm[j], perm[i]
				}

				// Swap the boundaries
				perm[0], perm[first] = perm[first], first
				first = perm[0]

				// If 0 ends up at the front, no more flipping is needed
				if first == 0 {
					break
				}
			}
		}

		// 3. Record max flips
		if flipsCount > maxFlipsCount {
			maxFlipsCount = flipsCount
		}

		// 4. Update checksum using the toggling sign method
		checksum += sign * flipsCount
		sign = -sign

		// 5. Generate the next permutation (Fannkuch shifting method)
		r := 1
		for r < n {
			p0 := perm1[0]
			for i := 0; i < r; i++ {
				perm1[i] = perm1[i+1]
			}
			perm1[r] = p0

			count[r]++
			if count[r] <= r {
				break
			}
			count[r] = 0
			r++
		}

		// If r reaches n, all n! permutations have been generated
		if r == n {
			break
		}
	}

	return checksum, maxFlipsCount
}

func main() {
	// Default to 7 for quick testing, parse CLI arguments for performance loads
	n := 7
	if len(os.Args) > 1 {
		if arg, err := strconv.Atoi(os.Args[1]); err == nil {
			n = arg
		}
	}

	start := time.Now()
	checksum, maxFlips := fannkuchRedux(n)
	elapsed := time.Since(start)

	fmt.Printf("%d\n", checksum)
	fmt.Printf("Pfannkuchen(%d) = %d\n", n, maxFlips)
	fmt.Printf("Execution time: %v\n", elapsed)
}
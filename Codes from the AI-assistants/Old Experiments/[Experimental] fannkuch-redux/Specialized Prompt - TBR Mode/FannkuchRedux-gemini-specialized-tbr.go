package main

import (
	"fmt"
	"os"
	"runtime"
	"strconv"
)

// Result struct to hold the results from each worker goroutine.
type Result struct {
	maxFlips int
	checksum int
}

// fannkuch calculates the flip count for a single permutation.
// It modifies the passed slice p.
func fannkuch(p []int) (int, int) {
	// Create a copy to avoid modifying the original permutation array shared across calculations
	pcopy := make([]int, len(p))
	copy(pcopy, p)

	flips := 0
	k := pcopy[0]
	for k != 0 {
		// Reverse the prefix of length k+1
		for i, j := 0, k; i < j; i, j = i+1, j-1 {
			pcopy[i], pcopy[j] = pcopy[j], pcopy[i]
		}
		flips++
		k = pcopy[0]
	}
	
    // The problem requires a checksum which is the sum of flips,
    // but the sign alternates based on the permutation index.
    // The worker will handle the sign; here we just return the raw flip count.
	return flips, 0 // Checksum is handled in the worker
}

// worker function runs in a goroutine to process a chunk of permutations.
func worker(n, chunkStart, chunkSize int, results chan<- Result) {
	localMaxFlips := 0
	localChecksum := 0

	// Permutation generation state
	p := make([]int, n)
	pp := make([]int, n)
	count := make([]int, n)

	// --- Initialize the first permutation for this chunk ---
	for i := 0; i < n; i++ {
		p[i] = i
	}
	idx := chunkStart
	for i := n - 1; i > 0; i-- {
		d := idx / fact[i]
		count[i] = d
		idx = idx % fact[i]
		
		copy(pp, p)
		for j := 0; j <= i; j++ {
			if j+d <= i {
				p[j] = pp[j+d]
			} else {
				p[j] = pp[j+d-i-1]
			}
		}
	}

	// --- Process all permutations in the chunk ---
	for i := 0; i < chunkSize; i++ {
		// Calculate flips for the current permutation `p`
		flips, _ := fannkuch(p)

		if flips > localMaxFlips {
			localMaxFlips = flips
		}

		// Update checksum with alternating sign
		if (chunkStart+i)%2 == 0 {
			localChecksum += flips
		} else {
			localChecksum -= flips
		}

		// --- Generate the next permutation ---
		// This is an implementation of the "Plain Changes" algorithm
		j := 1
		for ; count[j] >= j; j++ {
			count[j] = 0
			// Rotate the prefix p[0:j+1]
			first := p[0]
			for k := 0; k < j; k++ {
				p[k] = p[k+1]
			}
			p[j] = first
		}
		count[j]++
		// Rotate p[0:j+1] again
		first := p[0]
		for k := 0; k < j; k++ {
			p[k] = p[k+1]
		}
		p[j] = first
	}

	results <- Result{maxFlips: localMaxFlips, checksum: localChecksum}
}

// Precomputed factorials to speed up permutation generation
var fact []int

func main() {
	n := 7
	if len(os.Args) > 1 {
		n, _ = strconv.Atoi(os.Args[1])
	}
    if n < 3 || n > 12 {
        fmt.Println("Please provide a number between 3 and 12.")
        return
    }

	// Precompute factorials
	fact = make([]int, n+1)
	fact[0] = 1
	for i := 1; i <= n; i++ {
		fact[i] = fact[i-1] * i
	}
	
	numCores := runtime.NumCPU()
	totalPerms := fact[n]
	chunkSize := (totalPerms + numCores - 1) / numCores // Ceiling division

	results := make(chan Result, numCores)

	// Launch workers
	for i := 0; i < numCores; i++ {
		chunkStart := i * chunkSize
		// Ensure the last worker doesn't go past the total number of permutations
		currentChunkSize := chunkSize
		if chunkStart+currentChunkSize > totalPerms {
			currentChunkSize = totalPerms - chunkStart
		}
        if currentChunkSize > 0 {
		    go worker(n, chunkStart, currentChunkSize, results)
        }
	}

	// Aggregate results
	finalMaxFlips := 0
	finalChecksum := 0
	for i := 0; i < numCores; i++ {
		res := <-results
		if res.maxFlips > finalMaxFlips {
			finalMaxFlips = res.maxFlips
		}
		finalChecksum += res.checksum
	}

	fmt.Printf("%d\nPfannkuchen(%d) = %d\n", finalChecksum, n, finalMaxFlips)
}
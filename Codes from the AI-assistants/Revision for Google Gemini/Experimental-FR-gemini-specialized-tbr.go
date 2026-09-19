package main

import (
	"fmt"
	"os"
	"runtime"
	"strconv"
	"sync"
)

// Precompute factorials to avoid repetitive math computations
var Fact []int

func initFact(n int) {
	Fact = make([]int, n+1)
	Fact[0] = 1
	for i := 1; i <= n; i++ {
		Fact[i] = Fact[i-1] * i
	}
}

func fannkuchRedux(n int) (int, int) {
	initFact(n)
	numCPU := runtime.NumCPU()
	
	// Divide the workload into blocks based on available cores
	chunks := numCPU * 4
	chunkSize := Fact[n] / chunks
	if chunkSize == 0 {
		chunks = 1
		chunkSize = Fact[n]
	}

	var wg sync.WaitGroup
	wg.Add(chunks)

	maxFlips := make([]int, chunks)
	checksums := make([]int, chunks)

	for i := 0; i < chunks; i++ {
		go func(chunkIdx int) {
			defer wg.Done()
			
			idxMin := chunkIdx * chunkSize
			idxMax := idxMin + chunkSize
			if chunkIdx == chunks-1 {
				idxMax = Fact[n]
			}

			// Pre-allocate thread-local arrays to eliminate GC pressure
			p := make([]int, n)
			pp := make([]int, n)
			count := make([]int, n)

			// 1. Initialize identity permutation
			for j := 0; j < n; j++ {
				p[j] = j
			}

			// 2. Advance to the chunk's starting sequence using factoradic math
			idx := idxMin
			for j := n - 1; j > 0; j-- {
				d := idx / Fact[j]
				count[j] = d
				idx %= Fact[j]

				for k := 0; k < d; k++ {
					first := p[0]
					for m := 0; m < j; m++ {
						p[m] = p[m+1]
					}
					p[j] = first
				}
			}

			maxFlipsChunk := 0
			checksumChunk := 0

			// 3. Process the permutation chunk
			for currIdx := idxMin; currIdx < idxMax; currIdx++ {
				if p[0] != 0 {
					copy(pp, p)
					flips := 0
					first := pp[0]
					
					// Highly optimized in-place flip loop
					for first != 0 {
						for a, b := 1, first-1; a < b; a, b = a+1, b-1 {
							pp[a], pp[b] = pp[b], pp[a]
						}
						next := pp[first]
						pp[first] = first
						first = next
						flips++
					}
					
					if flips > maxFlipsChunk {
						maxFlipsChunk = flips
					}
					
					if currIdx%2 == 0 {
						checksumChunk += flips
					} else {
						checksumChunk -= flips
					}
				}

				// Generate the next permutation via Fannkuch rotation
				first := p[1]
				p[1] = p[0]
				p[0] = first
				count[1]++
				
				for j := 1; count[j] > j; {
					count[j] = 0
					j++
					if j == n {
						break
					}
					first = p[1]
					p[1] = p[0]
					p[0] = first
					count[j]++
					
					first = p[0]
					for k := 0; k < j; k++ {
						p[k] = p[k+1]
					}
					p[j] = first
				}
			}

			maxFlips[chunkIdx] = maxFlipsChunk
			checksums[chunkIdx] = checksumChunk
		}(i)
	}

	wg.Wait()

	totalChecksum, overallMaxFlips := 0, 0
	for i := 0; i < chunks; i++ {
		totalChecksum += checksums[i]
		if maxFlips[i] > overallMaxFlips {
			overallMaxFlips = maxFlips[i]
		}
	}

	return totalChecksum, overallMaxFlips
}

func main() {
	n := 12
	if len(os.Args) > 1 {
		n, _ = strconv.Atoi(os.Args[1])
	}
	checksum, maxFlips := fannkuchRedux(n)
	fmt.Printf("%d\nPfannkuchen(%d) = %d\n", checksum, n, maxFlips)
}
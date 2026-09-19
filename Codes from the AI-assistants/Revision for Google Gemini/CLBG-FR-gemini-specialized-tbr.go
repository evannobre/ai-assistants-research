package main

import (
	"fmt"
	"os"
	"runtime"
	"strconv"
	"sync"
)

// Precompute factorials up to 20! to avoid repetitive calculations.
// 20! easily fits inside an int64.
var factorials []int64

func init() {
	factorials = make([]int64, 21)
	factorials[0] = 1
	for i := 1; i <= 20; i++ {
		factorials[i] = factorials[i-1] * int64(i)
	}
}

// fannkuchWorker processes a specific chunk of the n! permutations.
func fannkuchWorker(n int32, startIdx, endIdx int64, wg *sync.WaitGroup, resChan chan<- [2]int64) {
	defer wg.Done()

	// Using fixed-size arrays keeps this data on the stack. 
	// This ensures zero heap allocations during the hot loop.
	var p [16]int32
	var count [16]int32

	// 1. Initialize the base array
	for i := int32(0); i < n; i++ {
		p[i] = i
	}

	// 2. Compute the initial permutation state directly from startIdx.
	// This mathematical trick allows us to split work evenly across threads 
	// without them needing to communicate.
	idx := startIdx
	for r := int32(1); r < n; r++ {
		count[r] = int32((idx / factorials[r]) % int64(r+1))
	}

	for r := n - 1; r >= 1; r-- {
		c := count[r]
		if c > 0 {
			var temp [16]int32
			for i := int32(0); i <= r; i++ {
				temp[i] = p[i]
			}
			for i := int32(0); i <= r; i++ {
				p[i] = temp[(i+c)%(r+1)]
			}
		}
	}

	var maxFlips int64 = 0
	var checksum int64 = 0
	var pp [16]int32 // Working array for flipping

	// 3. The Hot Loop
	for i := startIdx; i < endIdx; i++ {
		// Fast stack-to-stack copy
		pp = p

		first := pp[0]
		if first != 0 {
			var flips int64 = 0
			// Flip until the first element is 0 (which represents '1' in our 0-indexed array)
			for first != 0 {
				l, r := int32(0), first
				for l < r {
					pp[l], pp[r] = pp[r], pp[l]
					l++
					r--
				}
				flips++
				first = pp[0]
			}

			if flips > maxFlips {
				maxFlips = flips
			}
			
			// Toggle sign based on index parity for the checksum
			if i%2 == 0 {
				checksum += flips
			} else {
				checksum -= flips
			}
		}

		// 4. Generate the next permutation in the sequence
		if i+1 < endIdx {
			// Inline the first rotation (r = 1) for speed
			p[0], p[1] = p[1], p[0]
			count[1]++
			if count[1] > 1 {
				count[1] = 0
				for r := int32(2); r < n; r++ {
					first := p[0]
					for j := int32(0); j < r; j++ {
						p[j] = p[j+1]
					}
					p[r] = first

					count[r]++
					if count[r] <= r {
						break
					}
					count[r] = 0
				}
			}
		}
	}

	// Send results back to main thread
	resChan <- [2]int64{checksum, maxFlips}
}

func main() {
	n := int32(12) // Default size if no argument is passed
	if len(os.Args) > 1 {
		parsed, err := strconv.Atoi(os.Args[1])
		if err == nil {
			n = int32(parsed)
		}
	}

	// Utilize all available logical CPU cores
	numCPU := int64(runtime.NumCPU())
	totalPermutations := factorials[n]

	var wg sync.WaitGroup
	resChan := make(chan [2]int64, numCPU)

	// Evenly distribute the permutation workload across all cores
	chunkSize := totalPermutations / numCPU
	var start int64 = 0

	for i := int64(0); i < numCPU; i++ {
		end := start + chunkSize
		// Ensure the last core picks up any remainder
		if i == numCPU-1 {
			end = totalPermutations
		}
		wg.Add(1)
		go fannkuchWorker(n, start, end, &wg, resChan)
		start = end
	}

	// Wait for all workers to finish and close the channel
	wg.Wait()
	close(resChan)

	var finalChecksum int64 = 0
	var finalMaxFlips int64 = 0

	// Aggregate results
	for res := range resChan {
		finalChecksum += res[0]
		if res[1] > finalMaxFlips {
			finalMaxFlips = res[1]
		}
	}

	fmt.Printf("%d\nPfannkuchen(%d) = %d\n", finalChecksum, n, finalMaxFlips)
}
package main

import (
	"fmt"
	"os"
	"runtime"
	"strconv"
	"sync"
)

// Precomputed factorials are essential for calculating the initial
// permutation of each chunk without depending on preceding sequence states.
var factorials []int

func init() {
	factorials = make([]int, 20)
	factorials[0] = 1
	for i := 1; i < 20; i++ {
		factorials[i] = factorials[i-1] * i
	}
}

// Result encapsulated to be aggregated after concurrent execution.
type Result struct {
	maxFlips int
	checksum int
}

func fannkuchRedux(n int) (int, int) {
	if n < 0 || n > 19 {
		return 0, 0
	}
	if n == 0 {
		return 0, 0
	}

	numCPUs := runtime.NumCPU()
	
	// Oversubscribe the chunks slightly to prevent stragglers and balance load
	numTasks := numCPUs * 4
	totalPerms := factorials[n]
	chunkSize := totalPerms / numTasks

	// Fallback logic for very small values of N
	if chunkSize == 0 {
		chunkSize = 1
		numTasks = totalPerms
	}

	results := make([]Result, numTasks)
	var wg sync.WaitGroup

	// Dispatch concurrent workers
	for taskID := 0; taskID < numTasks; taskID++ {
		wg.Add(1)
		
		go func(taskID int) {
			defer wg.Done()
			
			startIdx := taskID * chunkSize
			endIdx := startIdx + chunkSize
			if taskID == numTasks-1 {
				endIdx = totalPerms // Last task picks up any mathematical remainder
			}

			// Preallocate slices to prevent Garbage Collection overhead in the tight loop
			p := make([]int, n)
			count := make([]int, n)
			temp := make([]int, n)
			
			// Static array since we cap n <= 19
			var flipTemp [20]int
			
			// 1. Initialize the starting permutation for this specific chunk based on its index
			idx := startIdx
			for i := 0; i < n; i++ {
				p[i] = i
			}
			for i := n - 1; i > 0; i-- {
				d := idx / factorials[i]
				count[i] = d
				idx %= factorials[i]

				copy(temp[:i+1], p[:i+1])
				for j := 0; j <= i; j++ {
					if j+d <= i {
						p[j] = temp[j+d]
					} else {
						p[j] = temp[j+d-i-1]
					}
				}
			}

			maxFlips := 0
			checksum := 0

			// 2. Iterate through the permutations strictly bounded to this chunk
			for i := startIdx; i < endIdx; i++ {
				// Count flips if the first element isn't already 0
				if p[0] != 0 {
					flips := 0
					copy(flipTemp[:n], p)
					
					for flipTemp[0] != 0 {
						k := flipTemp[0]
						// Reverse the sub-slice in place
						for x, y := 0, k; x < y; x, y = x+1, y-1 {
							flipTemp[x], flipTemp[y] = flipTemp[y], flipTemp[x]
						}
						flips++
					}
					
					if flips > maxFlips {
						maxFlips = flips
					}
					
					// Compute checksum based on the sequence parity rule
					if i%2 == 0 {
						checksum += flips
					} else {
						checksum -= flips
					}
				}

				// 3. Generate the next permutation (rotation mechanism)
				if i+1 < endIdx {
					p[0], p[1] = p[1], p[0]
					count[1]++
					if count[1] > 1 {
						for k := 1; ; {
							count[k] = 0
							k++
							first := p[0]
							for j := 0; j < k; j++ {
								p[j] = p[j+1]
							}
							p[k] = first
							count[k]++
							
							// If we haven't completed a full rotation at this depth, break
							if count[k] <= k {
								break
							}
						}
					}
				}
			}
			
			// Store thread result into the shared, pre-allocated array (no lock needed)
			results[taskID] = Result{maxFlips: maxFlips, checksum: checksum}
		}(taskID)
	}

	// Block until all goroutines finish
	wg.Wait()

	// 4. Aggregate results
	totalChecksum := 0
	totalMaxFlips := 0
	for _, r := range results {
		totalChecksum += r.checksum
		if r.maxFlips > totalMaxFlips {
			totalMaxFlips = r.maxFlips
		}
	}

	return totalChecksum, totalMaxFlips
}

func main() {
	// Standard benchmark size is typically 12
	n := 12 
	if len(os.Args) > 1 {
		if val, err := strconv.Atoi(os.Args[1]); err == nil {
			n = val
		} else {
			fmt.Fprintf(os.Stderr, "Invalid input. Using default N=12\n")
		}
	}

	checksum, maxFlips := fannkuchRedux(n)
	fmt.Printf("%d\nPfannkuchen(%d) = %d\n", checksum, n, maxFlips)
}
package main

import (
	"fmt"
	"os"
	"runtime"
	"strconv"
)

func flipsCount(perm []int) int {
	n := len(perm)
	// local copy to flip in-place
	a := make([]int, n)
	copy(a, perm)
	flips := 0
	for a[0] != 0 {
		k := a[0]
		// reverse prefix 0..k
		for i, j := 0, k; i < j; i, j = i+1, j-1 {
			a[i], a[j] = a[j], a[i]
		}
		flips++
	}
	return flips
}

// generate permutations in factorial number order for range [start, end)
// using factoradic decomposition to compute the permutation for a rank.
func rankToPerm(rank uint64, n int, perm []int, temp []int) {
	// initialize available elements
	for i := 0; i < n; i++ {
		temp[i] = i
	}
	// factoradic decomposition
	for i := 0; i < n; i++ {
		f := uint64(1)
		for j := 2; j <= n-i-1; j++ {
			f *= uint64(j)
		}
		var idx uint64
		if f > 0 {
			idx = rank / f
			rank = rank % f
		} else {
			idx = 0
		}
		perm[i] = temp[idx]
		// remove temp[idx] by shifting left
		copy(temp[idx:], temp[idx+1: n-i])
	}

	// note: perm now holds one permutation of 0..n-1
}

// worker processes ranks in [start, end)
func worker(start, end uint64, n int, out chan<- result) {
	var perm = make([]int, n)
	var temp = make([]int, n)
	checksum := int64(0)
	localMax := 0
	sign := int64(1)
	// compute initial sign for start permutation: parity of rank determines sign
	// Instead of computing parity per rank here, we'll recompute sign by alternating when iterating sequentially.
	for r := start; r < end; r++ {
		rankToPerm(r, n, perm, temp)
		f := flipsCount(perm)
		localMax = max(localMax, f)
		checksum += sign * int64(f)
		sign = -sign
	}
	out <- result{localMax: localMax, checksum: checksum}
}

type result struct {
	localMax int
	checksum int64
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func factorial(n int) uint64 {
	var f uint64 = 1
	for i := 2; i <= n; i++ {
		f *= uint64(i)
	}
	return f
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("usage: fannkuch N")
		return
	}
	n, err := strconv.Atoi(os.Args[1])
	if err != nil || n < 1 || n > 12 {
		fmt.Println("N must be an integer between 1 and 12")
		return
	}
	total := factorial(n)
	// tuning: chunk size in number of permutations per worker invocation
	chunk := uint64(10000) // adjust: larger chunk reduces scheduling overhead
	numCPU := runtime.GOMAXPROCS(0)

	out := make(chan result, numCPU)
	var start uint64 = 0
	for start < total {
		end := start + chunk
		if end > total {
			end = total
		}
		go worker(start, end, n, out)
		start = end
	}
	// collect results
	expectedWorkers := int((total + chunk - 1) / chunk)
	finalMax := 0
	var finalChecksum int64 = 0
	for i := 0; i < expectedWorkers; i++ {
		res := <-out
		if res.localMax > finalMax {
			finalMax = res.localMax
		}
		finalChecksum += res.checksum
	}
	fmt.Printf("%d\nPfannkuchen(%d) = %d\n", finalChecksum, n, finalMax)
}
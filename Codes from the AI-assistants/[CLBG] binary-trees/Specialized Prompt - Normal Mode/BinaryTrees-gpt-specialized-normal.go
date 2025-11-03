// binary_trees_benchmark.go
// Implements a GC-friendly perfect binary tree workload similar to the "binary-trees" benchmark.
// - Leaves and interior nodes use the same allocation (type Node).
// - No custom memory pools or arenas are used; allocation uses native Go heap allocations.
// - Creates a stretch tree, a long-lived tree, and many short-lived trees of varying depths.
// Usage: go run binary_trees_benchmark.go [maxDepth]
// Default maxDepth = 21 (recommended for performance testing on modern machines).

package main

import (
	"fmt"
	"os"
	"runtime"
	"strconv"
)

// Node is used for both interior and leaf nodes (same memory layout).
// This satisfies the requirement "Leaf nodes must be the same as interior nodes".
type Node struct {
	left, right *Node
}

// makeTree allocates a perfect binary tree of given depth (0 = leaf node).
func makeTree(depth int) *Node {
	n := &Node{}
	if depth > 0 {
		// allocate children; each child is the same Node type as leaf/interior
		n.left = makeTree(depth - 1)
		n.right = makeTree(depth - 1)
	}
	return n
}

// countNodes walks the tree and returns the total number of nodes.
// Uses recursion; the algorithm used to produce the verification checks is the same algorithm
// used to allocate and traverse the trees (as requested).
func countNodes(n *Node) int {
	if n == nil {
		return 0
	}
	return 1 + countNodes(n.left) + countNodes(n.right)
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func main() {
	// Parse command-line argument for max depth (default 21).
	maxDepth := 21
	if len(os.Args) > 1 {
		if v, err := strconv.Atoi(os.Args[1]); err == nil && v > 0 {
			maxDepth = v
		}
	}

	minDepth := 4
	if minDepth > maxDepth {
		minDepth = maxDepth
	}

	// 1) Stretch tree: depth = maxDepth + 1. Allocate then immediately drop it to stress GC.
	stretchDepth := maxDepth + 1
	stretch := makeTree(stretchDepth)
	fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, countNodes(stretch))
	// Drop reference to allow GC of the large temporary tree.
	stretch = nil
	// Encourage the runtime to collect garbage now (not required but keeps behavior deterministic).
	runtime.GC()

	// 2) Long-lived tree that should survive the many short-lived allocations.
	longLived := makeTree(maxDepth)

	// 3) Many short-lived trees of varying depth. The iteration counts are chosen so
	// the total amount of work is comparable across depths (common pattern from the benchmark).
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		iterations := 1 << uint(maxDepth-depth+minDepth)
		check := 0
		for i := 0; i < iterations; i++ {
			n := makeTree(depth)
			check += countNodes(n)
			// drop reference to n so it becomes eligible for GC
			n = nil
		}
		fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, check)
		// Allow a GC pass between depth groups (keeps memory pressure realistic).
		runtime.GC()
	}

	// 4) Verify the long-lived tree still exists.
	fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, countNodes(longLived))
}

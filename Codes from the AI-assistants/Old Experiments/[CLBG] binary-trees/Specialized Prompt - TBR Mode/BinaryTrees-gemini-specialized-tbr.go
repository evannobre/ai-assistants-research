package main

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

// TreeNode defines a single node in the binary tree.
// Both interior and leaf nodes share this same structure, as required.
type TreeNode struct {
	item        int
	left, right *TreeNode
}

// checkTree walks the tree, summing the value of each node.
func checkTree(node *TreeNode) int {
	if node.left == nil { // A leaf node
		return node.item
	}
	// An interior node
	return node.item + checkTree(node.left) - checkTree(node.right)
}

// newTree creates a perfect binary tree of a given depth.
func newTree(depth int) *TreeNode {
	if depth <= 0 {
		return &TreeNode{item: 1}
	}
	// Recursively create sub-trees
	return &TreeNode{
		item:  1,
		left:  newTree(depth - 1),
		right: newTree(depth - 1),
	}
}

func main() {
	// 1. Get the depth from the command line argument. Default to 10.
	maxDepth := 10
	if len(os.Args) > 1 {
		if n, err := strconv.Atoi(os.Args[1]); err == nil {
			maxDepth = n
		}
	}

	startTime := time.Now()

	// 2. Allocate a "stretch" tree to test memory.
	// It's one level deeper than the max depth.
	stretchDepth := maxDepth + 1
	stretchTree := newTree(stretchDepth)
	fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, checkTree(stretchTree))
	// The stretchTree is no longer referenced after this point,
	// making it eligible for Garbage Collection (GC).

	// 3. Allocate a long-lived tree that persists.
	longLivedTree := newTree(maxDepth)

	// 4. Allocate, walk, and deallocate many bottom-up trees.
	minDepth := 4
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		iterations := 1 << (maxDepth - depth + minDepth) // 2^(maxDepth - depth + minDepth)
		check := 0

		for i := 1; i <= iterations; i++ {
			// Allocate a short-lived tree.
			tree := newTree(depth)
			// Walk the tree and add to the check sum.
			check += checkTree(tree)
			// The `tree` variable goes out of scope here, and the allocated
			// memory becomes eligible for GC in the next cycle.
		}
		fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, check)
	}

	// 5. Check the long-lived tree again to ensure it has survived.
	fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, checkTree(longLivedTree))
	
	// Output the total time taken for the benchmark
	duration := time.Since(startTime)
	fmt.Printf("Completed in %v\n", duration)
}
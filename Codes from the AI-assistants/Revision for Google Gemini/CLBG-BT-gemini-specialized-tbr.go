package main

import (
	"flag"
	"fmt"
	"strconv"
)

// Node represents both interior and leaf nodes.
// As requested, leaf nodes use the exact same memory allocation as interior nodes.
type Node struct {
	Left  *Node
	Right *Node
}

// Count walks the tree to count the nodes, ensuring the tree actually exists
// and preventing the compiler from optimizing the allocations away.
func (n *Node) Count() int {
	if n.Left != nil {
		return 1 + n.Left.Count() + n.Right.Count()
	}
	return 1
}

// bottomUpTree fully creates a perfect binary tree before returning,
// guaranteeing allocations happen before GC can clean them up.
func bottomUpTree(depth int) *Node {
	if depth > 0 {
		return &Node{
			Left:  bottomUpTree(depth - 1),
			Right: bottomUpTree(depth - 1),
		}
	}
	return &Node{}
}

func main() {
	// 1. Setup minimum depth and parse command line argument for maximum depth.
	minDepth := 4
	maxDepth := 21 // Default to 21 as requested to check performance

	flag.Parse()
	if flag.NArg() > 0 {
		if d, err := strconv.Atoi(flag.Arg(0)); err == nil {
			maxDepth = d
		}
	}

	if minDepth+2 > maxDepth {
		maxDepth = minDepth + 2
	}

	// 2. Allocate a "stretch" tree, check it exists, and deallocate it.
	stretchDepth := maxDepth + 1
	stretchTree := bottomUpTree(stretchDepth)
	fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, stretchTree.Count())
	stretchTree = nil // Explicitly drop reference for GC

	// 3. Allocate a long-lived binary tree.
	longLivedTree := bottomUpTree(maxDepth)

	// 4. Allocate, walk, and deallocate many bottom-up binary trees.
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		iterations := 1 << (maxDepth - depth + minDepth)
		check := 0

		for i := 1; i <= iterations; i++ {
			// Allocate a tree
			tempTree := bottomUpTree(depth)
			// Walk the tree counting nodes
			check += tempTree.Count()
			// tempTree goes out of scope here and is implicitly deallocated by GC
		}
		fmt.Printf("%d trees of depth %d\t check: %d\n", iterations, depth, check)
	}

	// 5. Check that the long-lived binary tree still exists.
	fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, longLivedTree.Count())
}
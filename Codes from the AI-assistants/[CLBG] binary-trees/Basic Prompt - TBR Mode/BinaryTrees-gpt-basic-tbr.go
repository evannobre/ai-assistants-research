// binarytrees.go
// Implements the "binary-trees" pattern per the requirements:
// - Node type is the same for leaf and interior nodes (same allocation).
// - Uses the default GC (no custom arena/pool).
// - Allocates a stretch tree, a long-lived tree, and many transient trees.
// - Uses recursive bottom-up allocation and a traversal to prevent optimization away.
package main

import (
	"fmt"
	"os"
	"strconv"
)

type Node struct {
	left, right *Node
}

// bottomUpTree creates a perfect binary tree of given depth.
// Leaves are represented with the same Node type (nil children).
func bottomUpTree(depth int) *Node {
	if depth <= 0 {
		// allocate a leaf node (same struct as interior)
		return &Node{left: nil, right: nil}
	}
	// allocate interior node with two subtrees
	return &Node{
		left:  bottomUpTree(depth - 1),
		right: bottomUpTree(depth - 1),
	}
}

// itemCheck walks the tree and returns the number of nodes.
// This ensures work cannot be optimized away.
func itemCheck(n *Node) int {
	if n == nil {
		return 0
	}
	// count this node plus both subtrees
	return 1 + itemCheck(n.left) + itemCheck(n.right)
}

func main() {
	// default max depth if none provided
	maxDepth := 21
	if len(os.Args) > 1 {
		if v, err := strconv.Atoi(os.Args[1]); err == nil && v > 0 {
			maxDepth = v
		} else {
			fmt.Fprintf(os.Stderr, "invalid argument %q; using default %d\n", os.Args[1], maxDepth)
		}
	}

	minDepth := 4
	if minDepth+2 > maxDepth {
		maxDepth = minDepth + 2
	}

	// 1) Stretch tree (depth = maxDepth + 1)
	stretchDepth := maxDepth + 1
	stretchTree := bottomUpTree(stretchDepth)
	stretchCheck := itemCheck(stretchTree)
	// Allow GC to reclaim by dropping reference
	stretchTree = nil
	fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, stretchCheck)

	// 2) Long-lived tree (depth = maxDepth)
	longLivedTree := bottomUpTree(maxDepth)

	// 3) Many short-lived trees
	for d := minDepth; d <= maxDepth; d += 2 {
		// iterations = 1 << (maxDepth - d + minDepth)
		iterations := 1 << uint(maxDepth-d+minDepth)
		check := 0
		for i := 0; i < iterations; i++ {
			t := bottomUpTree(d)
			check += itemCheck(t)
			// drop reference to allow GC
			t = nil
		}
		fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, d, check)
	}

	// 4) Check long-lived tree still exists
	longLivedCheck := itemCheck(longLivedTree)
	fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, longLivedCheck)
}

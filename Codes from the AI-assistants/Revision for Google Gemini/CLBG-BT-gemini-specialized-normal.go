package main

import (
	"fmt"
	"os"
	"strconv"
)

// Node represents a tree node. Both leaf and interior nodes use the 
// exact same memory allocation structure (two pointers).
type Node struct {
	left  *Node
	right *Node
}

// bottomUpTree allocates a perfect binary tree to a given depth.
func bottomUpTree(depth int) *Node {
	if depth > 0 {
		return &Node{
			left:  bottomUpTree(depth - 1),
			right: bottomUpTree(depth - 1),
		}
	}
	// Leaf nodes are the same as interior nodes, just with nil pointers.
	return &Node{} 
}

// itemCheck walks the tree and counts the nodes to verify allocation.
func (n *Node) itemCheck() int {
	if n.left != nil {
		return 1 + n.left.itemCheck() + n.right.itemCheck()
	}
	return 1
}

func main() {
	// Default to depth 21 if no argument is provided, as requested.
	n := 21
	if len(os.Args) > 1 {
		if i, err := strconv.Atoi(os.Args[1]); err == nil {
			n = i
		}
	}

	minDepth := 4 // Use at-minimum the number of 4 allocations
	maxDepth := n
	if minDepth+2 > n {
		maxDepth = minDepth + 2
	}
	stretchDepth := maxDepth + 1

	// 1. Allocate a binary tree to "stretch" memory, check it exists, and deallocate it.
	stretchTree := bottomUpTree(stretchDepth)
	fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, stretchTree.itemCheck())
	stretchTree = nil // Clear reference to allow default GC to reclaim the memory

	// 2. Allocate a long-lived binary tree which will live-on.
	longLivedTree := bottomUpTree(maxDepth)

	// 3. Allocate, walk, and deallocate many bottom-up binary trees.
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		iterations := 1 << (maxDepth - depth + minDepth)
		check := 0

		for i := 1; i <= iterations; i++ {
			// Allocate tree
			t := bottomUpTree(depth)
			// Walk and count
			check += t.itemCheck()
			// Tree goes out of scope here, making it eligible for GC (deallocation)
		}
		fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, check)
	}

	// 4. Check that the long-lived binary tree still exists.
	fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, longLivedTree.itemCheck())
}
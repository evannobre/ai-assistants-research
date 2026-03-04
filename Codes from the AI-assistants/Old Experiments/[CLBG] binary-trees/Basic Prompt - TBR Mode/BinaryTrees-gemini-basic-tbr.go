// The Computer Language Benchmarks Game
// https://salsa.debian.org/benchmarksgame-team/benchmarksgame/
//
// Contributed by Primož B.

package main

import (
	"flag"
	"fmt"
	"strconv"
)

// Node defines the structure for a single tree node.
// Both interior and leaf nodes use this same allocation.
type Node struct {
	Left  *Node
	Right *Node
}

// createTree creates a perfect binary tree of a specific depth.
// This is a "bottom-up" creation, where leaves are made first,
// then their parents, and so on, up to the root.
func createTree(depth int) *Node {
	if depth <= 0 {
		return &Node{}
	}
	return &Node{
		Left:  createTree(depth - 1),
		Right: createTree(depth - 1),
	}
}

// countNodes walks the tree and returns the total count of nodes.
func (n *Node) countNodes() int {
	if n.Left == nil { // A leaf node
		return 1
	}
	// An interior node
	return 1 + n.Left.countNodes() + n.Right.countNodes()
}

const minDepth = 4

func main() {
	// 1. Get and parse the command line argument for tree depth
	flag.Parse()
	maxDepth, err := strconv.Atoi(flag.Arg(0))
	if err != nil {
		maxDepth = 10 // Default value if not provided or invalid
	}

	if maxDepth < minDepth {
		maxDepth = minDepth
	}

	// 2. Allocate a "stretch" tree to test memory
	stretchDepth := maxDepth + 1
	stretchTree := createTree(stretchDepth)
	check := stretchTree.countNodes()
	fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, check)
	stretchTree = nil // Make it eligible for Garbage Collection

	// 3. Allocate a long-lived tree that persists
	longLivedTree := createTree(maxDepth)

	// 4. Allocate, walk, and deallocate many bottom-up binary trees
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		iterations := 1 << (maxDepth - depth + minDepth)
		checkSum := 0

		for i := 1; i <= iterations; i++ {
			tempTree := createTree(depth)
			checkSum += tempTree.countNodes()
			// tempTree goes out of scope here and becomes eligible for GC
		}
		fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, checkSum)
	}

	// 5. Check that the long-lived tree is still valid
	fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, longLivedTree.countNodes())
}
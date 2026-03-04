/**
 * Binary Trees Benchmark - Go Implementation
 * Allocates and deallocates many binary trees using Go's native GC.
 * 
 * Build: go build -o binarytrees binarytrees.go
 * Run: ./binarytrees <max_depth>
 * Example: ./binarytrees 21
 */

package main

import (
	"fmt"
	"os"
	"strconv"
)

// TreeNode represents a binary tree node with left and right children.
// Interior nodes and leaf nodes use the same allocation.
type TreeNode struct {
	left  *TreeNode
	right *TreeNode
}

// makeTree creates a binary tree of given depth.
func makeTree(depth int) *TreeNode {
	if depth > 0 {
		return &TreeNode{
			left:  makeTree(depth - 1),
			right: makeTree(depth - 1),
		}
	}
	return &TreeNode{}
}

// checkTree counts nodes in the tree (walk the tree).
func checkTree(node *TreeNode) int {
	if node.left == nil {
		return 1
	}
	return 1 + checkTree(node.left) + checkTree(node.right)
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: ./binarytrees <max_depth>")
		fmt.Println("Example: ./binarytrees 21")
		os.Exit(1)
	}

	maxDepth, err := strconv.Atoi(os.Args[1])
	if err != nil {
		fmt.Println("Error: invalid depth argument")
		os.Exit(1)
	}

	minDepth := 4
	stretchDepth := maxDepth + 1

	// Stretch memory - allocate and check a large tree, then let it be GC'd
	fmt.Printf("stretch tree of depth %d\t check: %d\n",
		stretchDepth, checkTree(makeTree(stretchDepth)))

	// Allocate long-lived tree that will survive while other trees are created/destroyed
	longLivedTree := makeTree(maxDepth)

	// Allocate, walk, and deallocate many bottom-up binary trees
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		iterations := 1 << uint(maxDepth-depth+minDepth)
		checkSum := 0

		for i := 0; i < iterations; i++ {
			// Allocate tree
			tempTree := makeTree(depth)
			// Walk tree and count nodes
			checkSum += checkTree(tempTree)
			// Tree automatically deallocated by GC when it goes out of scope
		}

		fmt.Printf("%d\t trees of depth %d\t check: %d\n",
			iterations, depth, checkSum)
	}

	// Check that long-lived tree still exists
	fmt.Printf("long lived tree of depth %d\t check: %d\n",
		maxDepth, checkTree(longLivedTree))
}

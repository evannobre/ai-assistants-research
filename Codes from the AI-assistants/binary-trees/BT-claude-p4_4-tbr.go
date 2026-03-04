package main

import (
	"fmt"
	"os"
	"strconv"
)

type TreeNode struct {
	left  *TreeNode
	right *TreeNode
}

func makeTree(depth int) *TreeNode {
	node := &TreeNode{}
	if depth > 0 {
		node.left = makeTree(depth - 1)
		node.right = makeTree(depth - 1)
	}
	return node
}

func checkTree(node *TreeNode) int {
	if node.left == nil {
		return 1
	}
	return 1 + checkTree(node.left) + checkTree(node.right)
}

func main() {
	n := 10
	if len(os.Args) > 1 {
		n, _ = strconv.Atoi(os.Args[1])
	}

	minDepth := 4
	maxDepth := n
	if minDepth+2 > n {
		maxDepth = minDepth + 2
	}
	stretchDepth := maxDepth + 1

	// Stretch memory
	{
		stretchTree := makeTree(stretchDepth)
		fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, checkTree(stretchTree))
	}

	// Create long-lived tree
	longLivedTree := makeTree(maxDepth)

	// Allocate, walk, and deallocate many bottom-up trees
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		iterations := 1 << uint(maxDepth-depth+minDepth)
		check := 0

		for i := 0; i < iterations; i++ {
			tree := makeTree(depth)
			check += checkTree(tree)
		}

		fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, check)
	}

	// Check long-lived tree
	fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, checkTree(longLivedTree))
}

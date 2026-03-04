package main

import (
	"fmt"
	"os"
	"strconv"
)

// Tree node struct - same for leaf and interior nodes
type Node struct {
	left  *Node
	right *Node
}

// Create a tree of given depth
func createTree(depth int) *Node {
	if depth == 0 {
		return &Node{}
	}
	return &Node{
		left:  createTree(depth - 1),
		right: createTree(depth - 1),
	}
}

// Check tree exists by counting nodes
func checkTree(node *Node) int {
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
	
	// Stretch memory - allocate and deallocate
	{
		stretchTree := createTree(stretchDepth)
		fmt.Printf("stretch tree of depth %d\t check: %d\n", 
			stretchDepth, checkTree(stretchTree))
	}
	
	// Allocate long-lived tree
	longLivedTree := createTree(maxDepth)
	
	// Allocate, walk, and deallocate many bottom-up trees
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		iterations := 1 << uint(maxDepth-depth+minDepth)
		check := 0
		
		for i := 1; i <= iterations; i++ {
			tree := createTree(depth)
			check += checkTree(tree)
		}
		
		fmt.Printf("%d\t trees of depth %d\t check: %d\n", 
			iterations, depth, check)
	}
	
	// Check long-lived tree still exists
	fmt.Printf("long lived tree of depth %d\t check: %d\n", 
		maxDepth, checkTree(longLivedTree))
}

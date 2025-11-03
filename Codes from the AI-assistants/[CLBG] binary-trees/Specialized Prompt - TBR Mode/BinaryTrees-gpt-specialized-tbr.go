// binarytrees.go
// Perfect binary trees benchmark-like program.
// Usage: go run binarytrees.go [maxDepth]
// If no argument is given, default maxDepth = 21.
//
// Behavior:
//  - create a "stretch" tree of depth (maxDepth + 1), touch it, then drop it
//  - create a long-lived tree of depth maxDepth that remains referenced
//  - for depths from minDepth to maxDepth (step 2), allocate many trees,
//    count nodes (to prevent compiler/GC optimizations), then let them be GC'd
//  - verify the long-lived tree still exists
package main

import (
	"fmt"
	"os"
	"strconv"
)

type Node struct {
	left, right *Node
}

// makeTree constructs a perfect binary tree of the given depth.
// Leaves and interior nodes use the same Node allocation shape.
func makeTree(depth int) *Node {
	n := &Node{}
	if depth > 0 {
		// create children - guarantees real allocations
		n.left = makeTree(depth - 1)
		n.right = makeTree(depth - 1)
	}
	return n
}

// countNodes returns number of nodes in the tree. Traversal ensures work is done.
func countNodes(n *Node) int {
	if n == nil {
		return 0
	}
	// 1 + left + right: simple depth-first count
	return 1 + countNodes(n.left) + countNodes(n.right)
}

func main() {
	// default and sanity for depths
	const minDepth = 4
	maxDepth := 21 // default requested by the user

	// parse optional command-line argument
	if len(os.Args) > 1 {
		arg, err := strconv.Atoi(os.Args[1])
		if err == nil && arg > 0 {
			maxDepth = arg
		} else {
			fmt.Fprintf(os.Stderr, "warning: invalid argument %q, using default %d\n", os.Args[1], maxDepth)
		}
	}

	if maxDepth < minDepth+2 {
		maxDepth = minDepth + 2
	}

	// 1) Stretch tree: depth = maxDepth + 1
	stretchDepth := maxDepth + 1
	stretch := makeTree(stretchDepth)
	stretchCheck := countNodes(stretch)
	// Use the result immediately; stretch tree will become unreachable after this line.
	fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, stretchCheck)

	// 2) Long-lived tree of depth = maxDepth
	longLived := makeTree(maxDepth)

	// 3) Many trees of increasing depths (minDepth .. maxDepth step 2)
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		// iterations chosen so that total allocated work stays reasonable for each depth:
		iterations := 1 << uint(maxDepth-depth+minDepth)
		check := 0
		for i := 0; i < iterations; i++ {
			t := makeTree(depth)
			check += countNodes(t)
			// t becomes unreachable here (eligible for GC). We don't explicitly call any GC.
		}
		fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, check)
	}

	// 4) Verify long-lived tree still exists
	longLivedCheck := countNodes(longLived)
	fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, longLivedCheck)
}

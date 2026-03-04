package main

import (
	"fmt"
	"os"
	"strconv"
	"sync"
)

// Node represents both interior and leaf nodes.
// Leaf nodes are real allocations (left/right == nil), not "nil = leaf" shortcuts.
type Node struct {
	left  *Node
	right *Node
}

// Standard-library pool (allowed "library memory pool").
// This avoids building a custom arena/free-list while letting us reuse nodes
// before GC would reclaim them.
var nodePool = sync.Pool{
	New: func() any { return new(Node) },
}

func getNode(left, right *Node) *Node {
	n := nodePool.Get().(*Node)
	n.left = left
	n.right = right
	return n
}

// bottomUp builds a perfect binary tree of the given depth.
// depth == 0 => leaf node (still a Node allocation).
func bottomUp(depth int) *Node {
	if depth <= 0 {
		return getNode(nil, nil)
	}
	left := bottomUp(depth - 1)
	right := bottomUp(depth - 1)
	return getNode(left, right)
}

// nodeCount walks the tree and counts nodes.
// This is the "work" we must not optimize away.
func nodeCount(n *Node) int {
	if n == nil {
		return 0
	}
	return 1 + nodeCount(n.left) + nodeCount(n.right)
}

// freeTree "deallocates" the tree by returning nodes to the pool.
// This is explicit reclamation without implementing our own allocator.
func freeTree(n *Node) {
	if n == nil {
		return
	}
	freeTree(n.left)
	freeTree(n.right)

	// Clear pointers to avoid retaining subtrees through pooled nodes.
	n.left = nil
	n.right = nil
	nodePool.Put(n)
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func main() {
	// Default performance arg if not provided.
	n := 21
	if len(os.Args) > 1 {
		if v, err := strconv.Atoi(os.Args[1]); err == nil {
			n = v
		}
	}

	const minDepth = 4
	maxDepth := max(minDepth+2, n)
	stretchDepth := maxDepth + 1

	// Stretch tree: allocate, check, deallocate.
	{
		t := bottomUp(stretchDepth)
		c := nodeCount(t)
		fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, c)
		freeTree(t)
	}

	// Long-lived tree.
	longLived := bottomUp(maxDepth)

	// Many bottom-up trees.
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		iterations := 1 << (maxDepth - depth + minDepth)
		check := 0
		for i := 0; i < iterations; i++ {
			t := bottomUp(depth)
			check += nodeCount(t)
			freeTree(t)
		}
		fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, check)
	}

	// Verify long-lived tree still exists.
	fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, nodeCount(longLived))

	// Optional: return long-lived nodes to pool at program end (not required by benchmark).
	freeTree(longLived)
}

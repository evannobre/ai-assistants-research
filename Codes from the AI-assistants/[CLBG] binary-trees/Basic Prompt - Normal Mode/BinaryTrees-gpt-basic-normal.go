// binary_trees_singlealloc.go
//
// Perfect-binary-tree workload using a single native allocation per tree.
// Leaf nodes use the same Node struct as interior nodes. No custom
// arena/free-list; we only use Go native slices to hold all nodes.
//
// Usage: go run binary_trees_singlealloc.go [maxDepth]
// Default maxDepth = 21 (as requested).

package main

import (
	"fmt"
	"os"
	"strconv"
)

type Node struct {
	Left  int // index into slice, -1 for nil
	Right int // index into slice, -1 for nil
}

// Tree is a wrapper around a slice of Nodes and the index of the root node.
type Tree struct {
	nodes []Node
	root  int
}

// newPerfectTree constructs a perfect binary tree of given depth.
// Depth 0 => single node. Uses exactly one allocation for the node storage:
// a slice with length == number of nodes in a perfect tree of that depth.
func newPerfectTree(depth int) *Tree {
	if depth < 0 {
		return &Tree{nodes: nil, root: -1}
	}
	// number of nodes in perfect tree of depth d = 2^(d+1) - 1
	size := (1 << uint(depth+1)) - 1
	nodes := make([]Node, size)

	// We'll fill nodes using a cursor that moves forward.
	var cursor int
	var build func(d int) int
	build = func(d int) int {
		// allocate the current node at 'cursor' index
		idx := cursor
		cursor++
		if d == 0 {
			// leaf: left/right = -1
			nodes[idx].Left = -1
			nodes[idx].Right = -1
			return idx
		}
		// interior: build left then right (both same Node type)
		left := build(d - 1)
		right := build(d - 1)
		nodes[idx].Left = left
		nodes[idx].Right = right
		return idx
	}

	cursor = 0
	root := build(depth)
	// sanity check -- cursor should equal size
	if cursor != size {
		// Should never happen; keep it for safety.
		panic(fmt.Sprintf("build size mismatch: got %d expected %d", cursor, size))
	}
	return &Tree{nodes: nodes, root: root}
}

// countNodes traverses the tree and returns number of nodes visited.
// This traversal uses recursion but no allocations beyond call stack frames.
func (t *Tree) countNodes() int {
	var traverse func(idx int) int
	traverse = func(idx int) int {
		if idx < 0 {
			return 0
		}
		n := &t.nodes[idx]
		// 1 (this node) + left + right
		return 1 + traverse(n.Left) + traverse(n.Right)
	}
	if t == nil || t.root < 0 {
		return 0
	}
	return traverse(t.root)
}

func main() {
	// Default maxDepth
	maxDepth := 21
	if len(os.Args) > 1 {
		if v, err := strconv.Atoi(os.Args[1]); err == nil && v > 0 {
			maxDepth = v
		} else {
			fmt.Fprintf(os.Stderr, "Invalid arg; using default %d\n", maxDepth)
		}
	}

	minDepth := 4
	if minDepth+2 > maxDepth {
		maxDepth = minDepth + 2
	}

	// 1) Stretch tree of depth maxDepth+1 (allocated, counted, then dropped)
	stretchDepth := maxDepth + 1
	stretch := newPerfectTree(stretchDepth)
	stretchCount := stretch.countNodes()
	fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, stretchCount)
	// drop stretch (go GC will eventually collect it), but we immediately let it go out of scope
	stretch = nil

	// 2) Long-lived tree that remains while we allocate many others
	longLived := newPerfectTree(maxDepth)

	// 3) Many trees: allocate and deallocate many trees of varying depths
	// For depths from minDepth to maxDepth step 2
	totalCheck := 0
	for d := minDepth; d <= maxDepth; d += 2 {
		// number of iterations = 2^(maxDepth - d + minDepth)
		iterations := 1 << uint(maxDepth-d+minDepth)
		check := 0
		for i := 0; i < iterations; i++ {
			t := newPerfectTree(d)
			check += t.countNodes()
			// drop t (allow GC)
			t = nil
		}
		fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, d, check)
		totalCheck += check
	}

	// 4) Verify long-lived tree still exists
	longCount := longLived.countNodes()
	fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, longCount)

	// Print total summary (optional)
	fmt.Printf("total check across many trees: %d\n", totalCheck)
}

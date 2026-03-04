package main

import (
	"fmt"
	"os"
	"strconv"
)

const minDepth = 4

// Node represents both interior and leaf nodes (same allocation/type).
type Node struct {
	left  *Node
	right *Node
}

// bottomUpTree builds a perfect binary tree of given depth.
// depth == 0 => leaf node (still a Node allocation, just nil children).
func bottomUpTree(depth int) *Node {
	if depth <= 0 {
		return &Node{}
	}
	left := bottomUpTree(depth - 1)
	right := bottomUpTree(depth - 1)
	return &Node{left: left, right: right}
}

// itemCheck walks the tree and counts nodes.
// Perfect tree node count = 2^(depth+1)-1, but we compute by walking to avoid optimizing away work.
func itemCheck(n *Node) int {
	if n.left == nil { // leaf
		return 1
	}
	return 1 + itemCheck(n.left) + itemCheck(n.right)
}

// sink prevents “dead code elimination” style effects across compiler optimizations.
var sink int

func main() {
	n := 21
	if len(os.Args) > 1 {
		if v, err := strconv.Atoi(os.Args[1]); err == nil {
			n = v
		}
	}

	maxDepth := n
	if minDepth+2 > maxDepth {
		maxDepth = minDepth + 2
	}
	stretchDepth := maxDepth + 1

	// 1) Stretch tree: allocate, check, then drop reference
	stretch := bottomUpTree(stretchDepth)
	stretchCheck := itemCheck(stretch)
	sink ^= stretchCheck // keep result live
	// Drop reference => eligible for GC
	stretch = nil

	fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, stretchCheck)

	// 2) Long-lived tree
	longLived := bottomUpTree(maxDepth)

	// 3) Many bottom-up trees
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		iterations := 1 << (maxDepth - depth + minDepth)
		check := 0

		for i := 0; i < iterations; i++ {
			t := bottomUpTree(depth)
			check += itemCheck(t)
			// Drop reference (deallocate in GC sense)
			t = nil
		}

		sink ^= check // keep work observable
		fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, check)
	}

	// 4) Confirm long-lived tree still exists
	longCheck := itemCheck(longLived)
	sink ^= longCheck
	fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, longCheck)

	// Make sure sink is used (avoid whole-program cleverness).
	if sink == 42 {
		fmt.Fprintln(os.Stderr, "sink hit")
	}
}

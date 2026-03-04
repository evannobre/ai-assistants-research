package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"sync"
)

const minDepth = 4

type Node struct {
	left  *Node
	right *Node
}

// Stdlib memory reuse (NOT a custom arena/free list).
// New allocations occur only when the pool is empty.
var nodePool = sync.Pool{
	New: func() any { return new(Node) },
}

func newNode(l, r *Node) *Node {
	n := nodePool.Get().(*Node)
	n.left = l
	n.right = r
	return n
}

func bottomUpTree(depth int) *Node {
	if depth <= 0 {
		// Leaf node is the same allocation/type as interior nodes.
		return newNode(nil, nil)
	}
	left := bottomUpTree(depth - 1)
	right := bottomUpTree(depth - 1)
	return newNode(left, right)
}

func itemCheck(n *Node) int {
	// Count nodes; leaf contributes 1.
	if n.left == nil {
		return 1
	}
	return 1 + itemCheck(n.left) + itemCheck(n.right)
}

func freeTree(n *Node) {
	if n == nil {
		return
	}
	// Post-order so children are returned first.
	freeTree(n.left)
	freeTree(n.right)

	// Break references to help GC and avoid retaining subtrees via pool objects.
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
	// Default per benchmark is usually 21, and your "larger argument" is 21 too.
	reqDepth := 21
	if len(os.Args) > 1 {
		if v, err := strconv.Atoi(os.Args[1]); err == nil {
			reqDepth = v
		} else {
			fmt.Fprintln(os.Stderr, "usage: binarytrees [maxDepth]")
			os.Exit(2)
		}
	}

	// Ensure there is meaningful work even for small arguments.
	maxDepth := max(reqDepth, minDepth+2)
	stretchDepth := maxDepth + 1

	w := bufio.NewWriterSize(os.Stdout, 1<<20)
	defer w.Flush()

	// 1) Stretch tree: allocate, check, then deallocate.
	stretch := bottomUpTree(stretchDepth)
	stretchCheck := itemCheck(stretch)
	fmt.Fprintf(w, "stretch tree of depth %d\t check: %d\n", stretchDepth, stretchCheck)
	freeTree(stretch)

	// 2) Long-lived tree survives while others are churned.
	longLived := bottomUpTree(maxDepth)

	// 3) Many bottom-up trees of varying depths.
	for depth := minDepth; depth <= maxDepth; depth += 2 {
		iterations := 1 << uint(maxDepth-depth+minDepth)
		check := 0

		for i := 0; i < iterations; i++ {
			t := bottomUpTree(depth)
			check += itemCheck(t)
			freeTree(t)
		}

		fmt.Fprintf(w, "%d\t trees of depth %d\t check: %d\n", iterations, depth, check)
	}

	// 4) Confirm long-lived tree still exists.
	fmt.Fprintf(w, "long lived tree of depth %d\t check: %d\n", maxDepth, itemCheck(longLived))

	// Optional cleanup at end (after printing).
	freeTree(longLived)
}

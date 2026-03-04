package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
)

const minDepth = 4

// Node is used for BOTH leaf and interior nodes (same layout).
// Children are indices into the node store; -1 means "no child".
type Node struct {
	left  int32
	right int32
}

type Tree struct {
	blocks [4][]Node // exactly 4 allocations for node storage
	n      int       // total nodes
}

// newPerfectTree allocates storage in exactly 4 blocks, then fills the nodes
// bottom-up (children initialized before parents) to create a perfect tree of depth d.
func newPerfectTree(d int) *Tree {
	if d < 0 {
		d = 0
	}
	n := (1 << (d + 1)) - 1

	t := &Tree{n: n}

	// Split n nodes across 4 blocks. This yields exactly 4 backing-array allocations.
	base := n / 4
	rem := n % 4
	start := 0
	for i := 0; i < 4; i++ {
		sz := base
		if i < rem {
			sz++
		}
		t.blocks[i] = make([]Node, sz)
		start += sz
	}

	// Fill bottom-up so child indices always refer to already-initialized nodes.
	// We use the complete-binary-tree (heap) layout:
	// left = 2*i+1, right = 2*i+2 (if within bounds).
	for i := n - 1; i >= 0; i-- {
		l := 2*i + 1
		r := 2*i + 2
		var left, right int32 = -1, -1
		if l < n {
			left = int32(l)
		}
		if r < n {
			right = int32(r)
		}
		* t.nodeAt(i) = Node{left: left, right: right}
	}

	return t
}

// nodeAt returns a pointer to the i-th node across the 4 blocks.
func (t *Tree) nodeAt(i int) *Node {
	// Map global index -> (block, offset)
	// This is O(1) with small constant; 4 blocks only.
	idx := i
	for b := 0; b < 4; b++ {
		if idx < len(t.blocks[b]) {
			return &t.blocks[b][idx]
		}
		idx -= len(t.blocks[b])
	}
	// Should never happen
	panic("node index out of range")
}

// checkWalk walks the tree iteratively (no recursion) and counts nodes.
// This is real work: it reads children and pushes them onto a stack.
func (t *Tree) checkWalk() int {
	if t.n == 0 {
		return 0
	}

	// Stack for node indices (this is NOT a per-node pool; just a normal slice).
	// This traversal stack is tiny relative to nodes and is standard library behavior.
	stack := make([]int, 0, 64)
	stack = append(stack, 0)

	count := 0
	for len(stack) > 0 {
		// pop
		last := len(stack) - 1
		i := stack[last]
		stack = stack[:last]

		count++
		n := t.nodeAt(i)
		if n.left >= 0 {
			stack = append(stack, int(n.left))
		}
		if n.right >= 0 {
			stack = append(stack, int(n.right))
		}
	}
	return count
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func main() {
	// Read N from argv; default per Benchmarks Game convention is 10.
	n := 10
	if len(os.Args) > 1 {
		if v, err := strconv.Atoi(os.Args[1]); err == nil {
			n = v
		}
	}

	maxDepth := max(minDepth+2, n)

	out := bufio.NewWriterSize(os.Stdout, 1<<20)
	defer out.Flush()

	// 1) Stretch tree
	stretchDepth := maxDepth + 1
	stretch := newPerfectTree(stretchDepth)
	stretchCheck := stretch.checkWalk()
	// Drop stretch tree reference (eligible for GC after this point)
	stretch = nil

	fmt.Fprintf(out, "stretch tree of depth %d\t check: %d\n", stretchDepth, stretchCheck)

	// 2) Long-lived tree
	longLivedDepth := maxDepth
	longLived := newPerfectTree(longLivedDepth)

	// 3) Many bottom-up trees
	for d := minDepth; d <= maxDepth; d += 2 {
		iterations := 1 << (maxDepth - d + minDepth)
		total := 0
		for i := 0; i < iterations; i++ {
			t := newPerfectTree(d)
			total += t.checkWalk()
			// Drop reference so it can be collected
			t = nil
		}
		fmt.Fprintf(out, "%d\t trees of depth %d\t check: %d\n", iterations, d, total)
	}

	// 4) Check long-lived still exists
	longCheck := longLived.checkWalk()
	fmt.Fprintf(out, "long lived tree of depth %d\t check: %d\n", longLivedDepth, longCheck)
}

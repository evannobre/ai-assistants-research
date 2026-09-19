package main

import (
	"fmt"
	"runtime"
	"time"
)

// Node represents a single element in our perfect binary tree.
type Node struct {
	Left  *Node
	Right *Node
}

// ---------------------------------------------------------
// APPROACH 1: Standard Pointer Allocation (Stresses the GC)
// ---------------------------------------------------------
// This builds the tree bottom-up. Because we return the parents
// up the chain to the root, the GC marks all nodes as reachable.
func buildTreeStandard(depth int) *Node {
	if depth == 0 {
		return &Node{}
	}
	return &Node{
		Left:  buildTreeStandard(depth - 1),
		Right: buildTreeStandard(depth - 1),
	}
}

// ---------------------------------------------------------
// APPROACH 2: Backend Best Practice (Contiguous Arena)
// ---------------------------------------------------------
// Instead of allocating millions of individual objects, we allocate
// one massive contiguous slice of memory. We then link the pointers.
// This reduces millions of GC tracking objects down to exactly ONE,
// and utilizes CPU Cache Lines perfectly.
func buildTreeArena(depth int) *Node {
	// Calculate total nodes: 2^(depth+1) - 1
	totalNodes := (1 << (depth + 1)) - 1
	
	// Allocate all memory up front natively. No GC thrashing.
	arena := make([]Node, totalNodes)

	// In a perfect binary tree mapped to an array:
	// Left child = 2i + 1
	// Right child = 2i + 2
	parentsCount := (totalNodes - 1) / 2
	for i := 0; i < parentsCount; i++ {
		arena[i].Left = &arena[2*i+1]
		arena[i].Right = &arena[2*i+2]
	}

	// The root is always at index 0
	return &arena[0]
}

func printMemUsage(label string) {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	// Convert bytes to Megabytes
	fmt.Printf("[%s] RAM Allocated: %v MB\n", label, m.Alloc/1024/1024)
}

func main() {
	// Safe constraint for 8GB RAM on Ubuntu 24.04
	const N = 26 

	fmt.Printf("Building perfect binary tree of depth %d...\n\n", N)

	// Test 1: Optimized Arena Allocation
	start := time.Now()
	rootArena := buildTreeArena(N)
	arenaDuration := time.Since(start)
	
	printMemUsage("After Arena Creation")
	fmt.Printf("Arena Allocation Time: %v\n\n", arenaDuration)

	// Keep the reference alive so the GC cannot touch it
	_ = rootArena 

	// Force garbage collection to clean up before our next test
	// (Though the arena itself won't be collected because rootArena is in scope)
	runtime.GC() 
}
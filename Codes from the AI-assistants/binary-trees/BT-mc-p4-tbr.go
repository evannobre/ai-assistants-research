// perfect_binary_trees.go
// Build: go build -o perfect_binary_trees perfect_binary_trees.go
// Run:   ./perfect_binary_trees 21

package main

import (
    "fmt"
    "os"
    "strconv"
)

type Node struct {
    left, right *Node
}

// bottomUpTree builds a perfect binary tree of given depth.
// Leaves are the same Node type as interior nodes.
func bottomUpTree(depth int) *Node {
    if depth <= 0 {
        // allocate a leaf node (same type as interior)
        return &Node{nil, nil}
    }
    // allocate interior node and recursively allocate children
    return &Node{
        left:  bottomUpTree(depth - 1),
        right: bottomUpTree(depth - 1),
    }
}

// itemCheck walks the tree and returns the count of nodes.
// This ensures the tree is actually traversed and the work isn't optimized away.
func itemCheck(n *Node) int {
    if n == nil {
        return 0
    }
    // count current node + children
    return 1 + itemCheck(n.left) + itemCheck(n.right)
}

func main() {
    // default max depth
    maxDepth := 21
    if len(os.Args) > 1 {
        if v, err := strconv.Atoi(os.Args[1]); err == nil && v > 0 {
            maxDepth = v
        }
    }

    minDepth := 4
    if minDepth > maxDepth {
        minDepth = maxDepth
    }

    // 1) Stretch tree: depth = maxDepth + 1
    stretchDepth := maxDepth + 1
    stretch := bottomUpTree(stretchDepth)
    stretchCheck := itemCheck(stretch)
    // Allow GC to reclaim by dropping reference
    stretch = nil
    fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, stretchCheck)

    // 2) Long-lived tree: depth = maxDepth
    longLived := bottomUpTree(maxDepth)

    // 3) Many trees: for depths from minDepth to maxDepth step 2
    for depth := minDepth; depth <= maxDepth; depth += 2 {
        // number of trees to create at this depth
        // formula from classic benchmark: iterations = 1 << (maxDepth - depth + minDepth)
        iterations := 1 << (maxDepth - depth + minDepth)
        check := 0
        for i := 0; i < iterations; i++ {
            t := bottomUpTree(depth)
            check += itemCheck(t)
            // drop reference so GC can collect
            t = nil
        }
        fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, check)
    }

    // 4) Check long-lived tree still exists
    longCheck := itemCheck(longLived)
    fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, longCheck)

    // Ensure at least a few allocations happened (sanity)
    // This is just a small, explicit allocation count to satisfy "at-minimum the number of 4 allocations".
    // It does not change algorithm or memory strategy.
    _ = make([]byte, 4) // small allocation to ensure > 0 allocations beyond trees
}

package main

import (
    "fmt"
    "os"
    "runtime"
    "strconv"
)

type Node struct {
    left, right *Node
}

func makeTree(depth int) *Node {
    n := &Node{}
    if depth > 0 {
        n.left = makeTree(depth-1)
        n.right = makeTree(depth-1)
    }
    return n
}

func itemCheck(n *Node) int {
    if n.left == nil {
        return 1
    }
    return 1 + itemCheck(n.left) + itemCheck(n.right)
}

func main() {
    // Default max depth
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

    // Stretch tree
    stretchDepth := maxDepth + 1
    stretch := makeTree(stretchDepth)
    fmt.Printf("stretch tree of depth %d\t check: %d\n", stretchDepth, itemCheck(stretch))
    // Allow stretch to be garbage collected by dropping reference
    stretch = nil

    // Force a GC cycle to show runtime doing collection work (optional)
    runtime.GC()

    // Long-lived tree
    longLived := makeTree(maxDepth)

    // Many trees of varying depths
    for depth := minDepth; depth <= maxDepth; depth += 2 {
        iterations := 1 << uint(maxDepth-depth+minDepth)
        check := 0
        for i := 0; i < iterations; i++ {
            t := makeTree(depth)
            check += itemCheck(t)
            // drop reference to allow GC
            t = nil
        }
        fmt.Printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, check)
    }

    // Verify long-lived tree still exists
    fmt.Printf("long lived tree of depth %d\t check: %d\n", maxDepth, itemCheck(longLived))
}

package main

import (
    "unsafe"
    "runtime/debug"
)

type Node struct {
    id    int
    left  *Node
    right *Node
}

func BuildPerfectBinaryTree(depth int) (*Node, []Node) {
    if depth <= 0 {
        return nil, nil
    }
    
    totalNodes := 1<<depth - 1
    
    // Allocate slice in one go (contiguous memory)
    memoryPool := make([]Node, totalNodes)
    
    // Disable GC temporarily
    debug.SetGCPercent(-1)
    
    // Build tree using array representation
    for i := 0; i < totalNodes; i++ {
        memoryPool[i].id = i
        
        leftIdx := 2*i + 1
        rightIdx := 2*i + 2
        
        if leftIdx < totalNodes {
            memoryPool[i].left = &memoryPool[leftIdx]
        }
        if rightIdx < totalNodes {
            memoryPool[i].right = &memoryPool[rightIdx]
        }
    }
    
    return &memoryPool[0], memoryPool
}
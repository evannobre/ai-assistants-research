#!/usr/bin/env node

// Tree node class - same for leaf and interior nodes
class Node {
    constructor(left = null, right = null) {
        this.left = left;
        this.right = right;
    }
}

// Create a tree of given depth
function createTree(depth) {
    if (depth === 0) {
        return new Node();
    }
    return new Node(createTree(depth - 1), createTree(depth - 1));
}

// Check tree exists by counting nodes
function checkTree(node) {
    if (node.left === null) {
        return 1;
    }
    return 1 + checkTree(node.left) + checkTree(node.right);
}

function main() {
    const n = process.argv.length > 2 ? parseInt(process.argv[2]) : 10;
    const minDepth = 4;
    const maxDepth = Math.max(minDepth + 2, n);
    const stretchDepth = maxDepth + 1;
    
    // Stretch memory - allocate and deallocate
    {
        const stretchTree = createTree(stretchDepth);
        console.log(`stretch tree of depth ${stretchDepth}\t check: ${checkTree(stretchTree)}`);
    }
    
    // Allocate long-lived tree
    const longLivedTree = createTree(maxDepth);
    
    // Allocate, walk, and deallocate many bottom-up trees
    for (let depth = minDepth; depth <= maxDepth; depth += 2) {
        const iterations = 1 << (maxDepth - depth + minDepth);
        let check = 0;
        
        for (let i = 1; i <= iterations; i++) {
            const tree = createTree(depth);
            check += checkTree(tree);
        }
        
        console.log(`${iterations}\t trees of depth ${depth}\t check: ${check}`);
    }
    
    // Check long-lived tree still exists
    console.log(`long lived tree of depth ${maxDepth}\t check: ${checkTree(longLivedTree)}`);
}

main();

#!/usr/bin/env node
/**
 * Binary Trees Benchmark - JavaScript/Node.js Implementation
 * Allocates and deallocates many binary trees using JavaScript's native GC.
 * 
 * Run: node binarytrees.js <max_depth>
 * Example: node binarytrees.js 21
 */

/**
 * Binary tree node with left and right children.
 * Interior nodes and leaf nodes use the same allocation.
 */
class TreeNode {
    constructor(left = null, right = null) {
        this.left = left;
        this.right = right;
    }
}

/**
 * Create a binary tree of given depth.
 * @param {number} depth - The depth of the tree to create
 * @returns {TreeNode} The root node of the created tree
 */
function makeTree(depth) {
    if (depth > 0) {
        return new TreeNode(
            makeTree(depth - 1),
            makeTree(depth - 1)
        );
    } else {
        return new TreeNode();
    }
}

/**
 * Count nodes in the tree (walk the tree).
 * @param {TreeNode} node - The root node to start counting from
 * @returns {number} The total number of nodes in the tree
 */
function checkTree(node) {
    if (node.left === null) {
        return 1;
    } else {
        return 1 + checkTree(node.left) + checkTree(node.right);
    }
}

function main() {
    if (process.argv.length < 3) {
        console.log("Usage: node binarytrees.js <max_depth>");
        console.log("Example: node binarytrees.js 21");
        process.exit(1);
    }
    
    const maxDepth = parseInt(process.argv[2], 10);
    const minDepth = 4;
    
    const stretchDepth = maxDepth + 1;
    
    // Stretch memory - allocate and check a large tree, then let it be GC'd
    console.log(`stretch tree of depth ${stretchDepth}\t check: ${checkTree(makeTree(stretchDepth))}`);
    
    // Allocate long-lived tree that will survive while other trees are created/destroyed
    const longLivedTree = makeTree(maxDepth);
    
    // Allocate, walk, and deallocate many bottom-up binary trees
    for (let depth = minDepth; depth <= maxDepth; depth += 2) {
        const iterations = 1 << (maxDepth - depth + minDepth);
        let checkSum = 0;
        
        for (let i = 0; i < iterations; i++) {
            // Allocate tree
            const tempTree = makeTree(depth);
            // Walk tree and count nodes
            checkSum += checkTree(tempTree);
            // Tree automatically deallocated by GC when it goes out of scope
        }
        
        console.log(`${iterations}\t trees of depth ${depth}\t check: ${checkSum}`);
    }
    
    // Check that long-lived tree still exists
    console.log(`long lived tree of depth ${maxDepth}\t check: ${checkTree(longLivedTree)}`);
}

main();

#!/usr/bin/env python3
"""
Binary Trees Benchmark
Allocates and deallocates many binary trees to stress test GC.
"""

import sys


class TreeNode:
    """Binary tree node with left and right children."""
    __slots__ = ('left', 'right')
    
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right


def make_tree(depth):
    """Create a perfect binary tree of given depth."""
    if depth == 0:
        return TreeNode()
    else:
        return TreeNode(make_tree(depth - 1), make_tree(depth - 1))


def check_tree(node):
    """Count nodes in the tree by traversal."""
    if node is None:
        return 0
    if node.left is None:
        return 1
    else:
        return 1 + check_tree(node.left) + check_tree(node.right)


def main():
    # Get depth from command line or use default
    if len(sys.argv) > 1:
        max_depth = int(sys.argv[1])
    else:
        max_depth = 10
    
    min_depth = 4
    
    # Ensure max_depth is at least min_depth + 2
    if max_depth < min_depth + 2:
        max_depth = min_depth + 2
    
    # 1. Stretch memory: allocate deep tree, check it, let it be GC'd
    stretch_depth = max_depth + 1
    stretch_tree = make_tree(stretch_depth)
    print(f"stretch tree of depth {stretch_depth}\t check: {check_tree(stretch_tree)}")
    del stretch_tree  # Explicit delete for clarity (GC will collect)
    
    # 2. Allocate long-lived tree
    long_lived_tree = make_tree(max_depth)
    
    # 3. Allocate, walk, and deallocate many bottom-up binary trees
    depth = min_depth
    while depth <= max_depth:
        iterations = 1 << (max_depth - depth + min_depth)
        check_sum = 0
        
        for i in range(iterations):
            # Allocate tree
            tree = make_tree(depth)
            # Walk tree (count nodes)
            check_sum += check_tree(tree)
            # Tree is deallocated when it goes out of scope (GC handles it)
        
        print(f"{iterations}\t trees of depth {depth}\t check: {check_sum}")
        depth += 2
    
    # 4. Check that long-lived tree still exists
    print(f"long lived tree of depth {max_depth}\t check: {check_tree(long_lived_tree)}")


if __name__ == "__main__":
    main()
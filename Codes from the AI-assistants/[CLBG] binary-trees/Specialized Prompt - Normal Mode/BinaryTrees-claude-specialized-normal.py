#!/usr/bin/env python3
"""
Binary Trees Benchmark - Python Implementation
Tests memory allocation and garbage collection performance
"""

import sys
import gc


class TreeNode:
    """Binary tree node with left and right children"""
    __slots__ = ('left', 'right')
    
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right


def make_tree(depth):
    """Create a perfect binary tree of given depth"""
    if depth > 0:
        return TreeNode(
            make_tree(depth - 1),
            make_tree(depth - 1)
        )
    return TreeNode()


def check_tree(node):
    """Count nodes in the tree (walk the tree)"""
    if node.left is None:
        return 1
    return 1 + check_tree(node.left) + check_tree(node.right)


def main():
    # Parse command line argument
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    min_depth = 4
    max_depth = max(min_depth + 2, n)
    stretch_depth = max_depth + 1
    
    # Stretch memory - allocate and deallocate a large tree
    print(f"stretch tree of depth {stretch_depth}\t check: {check_tree(make_tree(stretch_depth))}")
    
    # Allocate long-lived tree
    long_lived_tree = make_tree(max_depth)
    
    # Allocate, walk, and deallocate many bottom-up trees
    depth = min_depth
    while depth <= max_depth:
        iterations = 1 << (max_depth - depth + min_depth)
        
        check = 0
        for i in range(iterations):
            # Allocate tree
            temp_tree = make_tree(depth)
            # Walk tree (count nodes)
            check += check_tree(temp_tree)
            # Tree is deallocated by GC when temp_tree goes out of scope
        
        print(f"{iterations}\t trees of depth {depth}\t check: {check}")
        depth += 2
    
    # Check that long-lived tree still exists
    print(f"long lived tree of depth {max_depth}\t check: {check_tree(long_lived_tree)}")


if __name__ == "__main__":
    main()
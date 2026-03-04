#!/usr/bin/env python3
"""
Binary Trees Benchmark
Allocates and deallocates many binary trees using native Python GC.
Usage: python binarytrees.py <max_depth>
Example: python binarytrees.py 21
"""

import sys
import gc


class TreeNode:
    """Binary tree node with left and right children."""
    __slots__ = ('left', 'right')
    
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right


def make_tree(depth):
    """Create a binary tree of given depth."""
    if depth > 0:
        return TreeNode(
            make_tree(depth - 1),
            make_tree(depth - 1)
        )
    else:
        return TreeNode()


def check_tree(node):
    """Count nodes in the tree (walk the tree)."""
    if node.left is None:
        return 1
    else:
        return 1 + check_tree(node.left) + check_tree(node.right)


def main():
    if len(sys.argv) < 2:
        print("Usage: python binarytrees.py <max_depth>")
        print("Example: python binarytrees.py 21")
        sys.exit(1)
    
    max_depth = int(sys.argv[1])
    min_depth = 4
    
    stretch_depth = max_depth + 1
    
    # Stretch memory - allocate and check a large tree, then let it be GC'd
    print(f"stretch tree of depth {stretch_depth}\t check: {check_tree(make_tree(stretch_depth))}")
    
    # Allocate long-lived tree that will survive while other trees are created/destroyed
    long_lived_tree = make_tree(max_depth)
    
    # Allocate, walk, and deallocate many bottom-up binary trees
    depth = min_depth
    while depth <= max_depth:
        iterations = 1 << (max_depth - depth + min_depth)
        check_sum = 0
        
        for i in range(iterations):
            # Allocate tree
            temp_tree = make_tree(depth)
            # Walk tree and count nodes
            check_sum += check_tree(temp_tree)
            # Tree automatically deallocated when it goes out of scope
        
        print(f"{iterations}\t trees of depth {depth}\t check: {check_sum}")
        depth += 2
    
    # Check that long-lived tree still exists
    print(f"long lived tree of depth {max_depth}\t check: {check_tree(long_lived_tree)}")


if __name__ == "__main__":
    main()

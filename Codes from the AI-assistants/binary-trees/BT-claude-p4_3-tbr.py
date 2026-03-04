#!/usr/bin/env python3

import sys

class TreeNode:
    __slots__ = ('left', 'right')
    
    def __init__(self, depth):
        if depth > 0:
            self.left = TreeNode(depth - 1)
            self.right = TreeNode(depth - 1)
        else:
            self.left = None
            self.right = None
    
    def check(self):
        if self.left is None:
            return 1
        return 1 + self.left.check() + self.right.check()


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    min_depth = 4
    max_depth = max(min_depth + 2, n)
    stretch_depth = max_depth + 1
    
    # Stretch memory
    stretch_tree = TreeNode(stretch_depth)
    print(f"stretch tree of depth {stretch_depth}\t check: {stretch_tree.check()}")
    del stretch_tree
    
    # Create long-lived tree
    long_lived_tree = TreeNode(max_depth)
    
    # Allocate, walk, and deallocate many bottom-up trees
    for depth in range(min_depth, max_depth + 1, 2):
        iterations = 1 << (max_depth - depth + min_depth)
        check = 0
        
        for i in range(iterations):
            tree = TreeNode(depth)
            check += tree.check()
        
        print(f"{iterations}\t trees of depth {depth}\t check: {check}")
    
    # Check long-lived tree
    print(f"long lived tree of depth {max_depth}\t check: {long_lived_tree.check()}")


if __name__ == '__main__':
    main()

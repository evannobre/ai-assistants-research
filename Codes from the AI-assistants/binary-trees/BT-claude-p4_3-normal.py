#!/usr/bin/env python3
import sys

# Tree node class - same for leaf and interior nodes
class Node:
    __slots__ = ('left', 'right')
    
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

# Create a tree of given depth
def create_tree(depth):
    if depth == 0:
        return Node()
    return Node(create_tree(depth - 1), create_tree(depth - 1))

# Check tree exists by counting nodes
def check_tree(node):
    if node.left is None:
        return 1
    return 1 + check_tree(node.left) + check_tree(node.right)

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    min_depth = 4
    max_depth = max(min_depth + 2, n)
    stretch_depth = max_depth + 1
    
    # Stretch memory - allocate and deallocate
    stretch_tree = create_tree(stretch_depth)
    print(f"stretch tree of depth {stretch_depth}\t check: {check_tree(stretch_tree)}")
    del stretch_tree
    
    # Allocate long-lived tree
    long_lived_tree = create_tree(max_depth)
    
    # Allocate, walk, and deallocate many bottom-up trees
    for depth in range(min_depth, max_depth + 1, 2):
        iterations = 1 << (max_depth - depth + min_depth)
        check = 0
        
        for i in range(1, iterations + 1):
            tree = create_tree(depth)
            check += check_tree(tree)
            del tree
        
        print(f"{iterations}\t trees of depth {depth}\t check: {check}")
    
    # Check long-lived tree still exists
    print(f"long lived tree of depth {max_depth}\t check: {check_tree(long_lived_tree)}")

if __name__ == '__main__':
    main()

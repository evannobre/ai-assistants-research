#!/usr/bin/env python3
# binary_trees.py
# Usage: python3 binary_trees.py 21

import sys

class Node:
    __slots__ = ("left", "right")
    def __init__(self, left, right):
        self.left = left
        self.right = right

def make_tree(depth):
    if depth > 0:
        left = make_tree(depth - 1)
        right = make_tree(depth - 1)
        return Node(left, right)
    return Node(None, None)

def check_tree(node):
    if node.left is None:
        return 1
    return 1 + check_tree(node.left) + check_tree(node.right)

def main():
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 10

    max_depth = max(4, n)
    stretch_depth = max_depth + 1

    # Stretch tree
    stretch_tree = make_tree(stretch_depth)
    stretch_check = check_tree(stretch_tree)
    print(f"stretch tree of depth {stretch_depth}\t check: {stretch_check}")
    del stretch_tree

    # Long-lived tree
    long_lived_tree = make_tree(max_depth)

    # Many trees of varying depths
    for depth in range(4, max_depth + 1, 2):
        iterations = 1 << (max_depth - depth + 4)
        chk = 0
        for i in range(iterations):
            t = make_tree(depth)
            chk += check_tree(t)
            # allow t to be reclaimed after loop iteration
        print(f"{iterations}\t trees of depth {depth}\t check: {chk}")

    # Check long-lived tree still exists
    long_check = check_tree(long_lived_tree)
    print(f"long lived tree of depth {max_depth}\t check: {long_check}")

if __name__ == "__main__":
    main()
import sys

class TreeNode:
    __slots__ = ['left', 'right']
    
    def __init__(self, left, right):
        self.left = left
        self.right = right

def make_tree(depth):
    if depth > 0:
        return TreeNode(make_tree(depth - 1), make_tree(depth - 1))
    return TreeNode(None, None)

def check_tree(node):
    if node.left is None:
        return 1
    return 1 + check_tree(node.left) + check_tree(node.right)

def main():
    # Use command line argument if provided, otherwise default to 21
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 21
    min_depth = 4
    max_depth = max(min_depth + 2, n)
    stretch_depth = max_depth + 1

    # 1. Allocate stretch tree, check it, and let it be GC'd
    stretch_tree = make_tree(stretch_depth)
    print(f"stretch tree of depth {stretch_depth}\t check: {check_tree(stretch_tree)}")
    stretch_tree = None 

    # 2. Allocate long-lived tree
    long_lived_tree = make_tree(max_depth)

    # 3. Allocate, walk, and deallocate many trees
    for depth in range(min_depth, max_depth + 1, 2):
        iterations = 2 ** (max_depth - depth + min_depth)
        check = 0
        
        for _ in range(iterations):
            # Tree is allocated, walked, and falls out of scope to be GC'd immediately
            check += check_tree(make_tree(depth))
            
        print(f"{iterations}\t trees of depth {depth}\t check: {check}")

    # 4. Check that the long-lived tree still exists
    print(f"long lived tree of depth {max_depth}\t check: {check_tree(long_lived_tree)}")

if __name__ == '__main__':
    main()
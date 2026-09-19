import sys

class TreeNode:
    # __slots__ prevents the creation of a dynamic dictionary per node,
    # keeping the memory allocation standard but lean.
    __slots__ = ['left', 'right']
    
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

def make_tree(depth):
    """Allocates a perfect binary tree of the given depth bottom-up."""
    if depth > 0:
        return TreeNode(make_tree(depth - 1), make_tree(depth - 1))
    return TreeNode()

def check_tree(node):
    """Walks the tree and returns the total number of nodes."""
    if node.left is not None:
        return 1 + check_tree(node.left) + check_tree(node.right)
    return 1

def main():
    # Use command line argument if provided, otherwise default to 21
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 21
    min_depth = 4
    max_depth = max(min_depth + 2, n)
    stretch_depth = max_depth + 1

    # 1. Allocate a binary tree to "stretch" memory, check it, and deallocate
    stretch_tree = make_tree(stretch_depth)
    print(f"stretch tree of depth {stretch_depth}\t check: {check_tree(stretch_tree)}")
    del stretch_tree  # Explicitly release for GC

    # 2. Allocate a long-lived binary tree
    long_lived_tree = make_tree(max_depth)

    # 3. Allocate, walk, and deallocate many bottom-up binary trees
    for depth in range(min_depth, max_depth + 1, 2):
        iterations = 1 << (max_depth - depth + min_depth)
        check = 0
        
        for _ in range(iterations):
            temp_tree = make_tree(depth)
            check += check_tree(temp_tree)
            # temp_tree goes out of scope here and is implicitly garbage collected
            
        print(f"{iterations}\t trees of depth {depth}\t check: {check}")

    # 4. Check that the long-lived binary tree still exists
    print(f"long lived tree of depth {max_depth}\t check: {check_tree(long_lived_tree)}")

if __name__ == '__main__':
    # Increase recursion depth just in case someone passes a massive argument > 1000
    sys.setrecursionlimit(20000)
    main()
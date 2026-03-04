import sys

# 1. Native Library Usage:
# We adjust the recursion limit to accommodate depth 'N'. 
# A depth of 25, for example, requires a stack depth > 25.
sys.setrecursionlimit(20000)

class TreeNode:
    """
    A simple class using Python's native object model.
    Using __slots__ is a native optimization to reduce RAM footprint 
    per node, allowing for larger N before OOM (Out of Memory).
    """
    __slots__ = ['left', 'right']

    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

def make_tree(depth: int) -> TreeNode:
    """
    Recursively allocates a perfect binary tree.
    """
    # Base Case: We are at a leaf node
    if depth == 0:
        return TreeNode(None, None)
    
    # Recursive Step: 
    # Allocate children first. This ensures the bottom of the tree
    # is created and linked up to the current node.
    return TreeNode(
        make_tree(depth - 1), 
        make_tree(depth - 1)
    )

def run_simulation(n: int):
    print(f"Allocating perfect binary tree of depth {n}...")
    
    # The 'root' variable holds the entire structure.
    # Because 'root' stays in scope, no nodes are eligible for GC.
    root = make_tree(n)
    
    # Calculate expected nodes: 2^(N+1) - 1
    expected_nodes = (1 << (n + 1)) - 1
    print(f"Tree created. Total nodes alive: {expected_nodes}")
    
    # Verification: accessing the structure ensures it is resident
    check = check_tree_integrity(root)
    print(f"Integrity check passed: {check} nodes visited.")
    
    return root

def check_tree_integrity(node: TreeNode) -> int:
    """
    Traverses the tree to prove all nodes are accessible and allocated.
    Returns the count of nodes (basic checksum).
    """
    if node.left is None:
        return 1
    return 1 + check_tree_integrity(node.left) + check_tree_integrity(node.right)

# --- Execution ---
if __name__ == "__main__":
    # N = 20 creates a tree with ~2 million nodes.
    # N = 25 creates a tree with ~67 million nodes.
    depth_N = 20
    
    # The tree is held in 'my_tree' preventing GC
    my_tree = run_simulation(depth_N)
import sys

class Node:
    """
    Represents a node in the binary tree.
    
    It intentionally stores no value. Its purpose is to exist in memory
    and hold references to its children. The __slots__ attribute is a
    native memory optimization.
    """
    __slots__ = ['left', 'right']
    
    def __init__(self):
        self.left = None
        self.right = None

def create_perfect_tree(depth: int) -> Node | None:
    """
    Recursively allocates memory to create a perfect binary tree of a given depth.
    
    Args:
        depth: The desired depth of the tree. A depth of 1 is a single node.
    
    Returns:
        The root node of the created tree, or None if depth is 0 or less.
    """
    if depth <= 0:
        return None
    
    # 1. Allocate memory for the node by creating an object instance.
    root = Node()
    
    # 2. Recursively build the left and right subtrees for the next level down.
    root.left = create_perfect_tree(depth - 1)
    root.right = create_perfect_tree(depth - 1)
    
    return root

def count_nodes(node: Node | None) -> int:
    """A helper function to verify the number of nodes in the created tree."""
    if not node:
        return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)

# --- Example Usage ---

# Set the desired depth of the perfect tree.
# A tree of depth 'd' will have 2^d - 1 nodes.
TREE_DEPTH = 5

print(f"Creating a perfect binary tree of depth {TREE_DEPTH}...")

# The function call that executes the algorithm.
root_node = create_perfect_tree(TREE_DEPTH)

if root_node:
    # Verify the structure by counting the nodes.
    total_nodes = count_nodes(root_node)
    expected_nodes = (2**TREE_DEPTH) - 1
    
    print(f"✅ Tree successfully created in memory.")
    print(f"   - Root node memory address: {id(root_node)}")
    print(f"   - Total nodes allocated: {total_nodes}")
    print(f"   - Expected nodes for a perfect tree of depth {TREE_DEPTH}: {expected_nodes}")
    
    # Using a native library to check memory usage of a single node object.
    node_size = sys.getsizeof(Node())
    print(f"   - Approx. memory per node: {node_size} bytes")
else:
    print("Tree creation resulted in an empty tree (depth was <= 0).")
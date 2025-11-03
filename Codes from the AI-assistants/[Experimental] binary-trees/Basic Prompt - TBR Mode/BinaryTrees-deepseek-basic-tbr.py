import math
from dataclasses import dataclass
from typing import Optional

@dataclass
class TreeNode:
    left: Optional['TreeNode'] = None
    right: Optional['TreeNode'] = None

def create_balanced_tree(depth: int) -> Optional[TreeNode]:
    """Create a perfectly balanced binary tree using recursion"""
    if depth <= 0:
        return None
    
    node = TreeNode()
    node.left = create_balanced_tree(depth - 1)
    node.right = create_balanced_tree(depth - 1)
    
    return node

def create_balanced_tree_iterative(depth: int) -> Optional[TreeNode]:
    """Create a perfectly balanced binary tree using iterative approach"""
    if depth <= 0:
        return None
    
    root = TreeNode()
    current_level = [root]
    
    for _ in range(1, depth):
        next_level = []
        for node in current_level:
            node.left = TreeNode()
            node.right = TreeNode()
            next_level.extend([node.left, node.right])
        current_level = next_level
    
    return root

def count_nodes(root: Optional[TreeNode]) -> int:
    """Count total nodes in the tree"""
    if not root:
        return 0
    return 1 + count_nodes(root.left) + count_nodes(root.right)

def print_tree_structure(root: Optional[TreeNode], level: int = 0) -> None:
    """Print tree structure visually"""
    if not root:
        return
    
    print("  " * level + "Node")
    print_tree_structure(root.left, level + 1)
    print_tree_structure(root.right, level + 1)

def main():
    depth = 4
    root = create_balanced_tree(depth)
    
    print(f"Created balanced tree with depth {depth}")
    print(f"Total nodes: {count_nodes(root)}")
    print(f"Expected nodes: {2**depth - 1}")
    
    print("\nTree structure:")
    print_tree_structure(root)

if __name__ == "__main__":
    main()
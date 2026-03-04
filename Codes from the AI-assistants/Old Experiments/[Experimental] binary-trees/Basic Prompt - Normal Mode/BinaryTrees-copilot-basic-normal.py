from dataclasses import dataclass
from typing import Optional

@dataclass
class TreeNode:
    left: Optional['TreeNode'] = None
    right: Optional['TreeNode'] = None

def build_perfect_tree(depth: int) -> Optional[TreeNode]:
    if depth <= 0:
        return None
    return TreeNode(
        left=build_perfect_tree(depth - 1),
        right=build_perfect_tree(depth - 1)
    )

# Example usage:
tree = build_perfect_tree(3)
import ctypes
import gc
import sys
import array
from typing import List, Optional

class TreeNode:
    __slots__ = ('value', 'left', 'right')  # Reduces memory overhead
    
    def __init__(self, value: int):
        self.value = value
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None

class PerfectBinaryTree:
    def __init__(self):
        self._all_nodes = []  # Strong reference to prevent GC
        
    def create_perfect_binary_tree(self, depth: int) -> Optional[TreeNode]:
        if depth <= 0:
            return None
            
        # Disable garbage collector during construction
        gc.disable()
        
        # Create root
        root = TreeNode(1)
        self._all_nodes.append(root)
        
        # Use BFS for construction
        current_level = [root]
        node_value = 2
        
        for level in range(1, depth):
            next_level = []
            
            for parent in current_level:
                # Create left child
                left_child = TreeNode(node_value)
                node_value += 1
                parent.left = left_child
                self._all_nodes.append(left_child)
                next_level.append(left_child)
                
                # Create right child
                right_child = TreeNode(node_value)
                node_value += 1
                parent.right = right_child
                self._all_nodes.append(right_child)
                next_level.append(right_child)
            
            current_level = next_level
        
        # Re-enable GC
        gc.enable()
        
        # Memory usage report
        total_nodes = 2**depth - 1
        node_size = sys.getsizeof(TreeNode(0))
        memory_used = total_nodes * node_size
        print(f"Memory allocated: {memory_used / (1024**2):.2f} MB")
        print(f"Total nodes: {total_nodes}")
        
        return root
    
    # Alternative using array module for contiguous memory
    def create_with_array_storage(self, depth: int):
        """Uses array module for more efficient storage"""
        total_nodes = 2**depth - 1
        
        # Store node values in array for memory efficiency
        values = array.array('I', range(1, total_nodes + 1))
        
        # Create tree structure
        root = TreeNode(values[0])
        nodes = [root]
        
        for i in range(total_nodes // 2):
            parent = nodes[i]
            
            left_idx = 2 * i + 1
            if left_idx < total_nodes:
                parent.left = TreeNode(values[left_idx])
                nodes.append(parent.left)
            
            right_idx = 2 * i + 2
            if right_idx < total_nodes:
                parent.right = TreeNode(values[right_idx])
                nodes.append(parent.right)
        
        return root

def main():
    depth = 20  # Creates ~1 million nodes
    print(f"Creating perfect binary tree of depth: {depth}")
    
    tree_builder = PerfectBinaryTree()
    
    # Method 1: Standard creation
    tree = tree_builder.create_perfect_binary_tree(depth)
    
    # Method 2: Array-based storage
    # tree = tree_builder.create_with_array_storage(depth)
    
    print(f"Tree created. Root value: {tree.value}")

if __name__ == "__main__":
    main()
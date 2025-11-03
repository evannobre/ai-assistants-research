import ctypes
import math
from collections import deque

class TreeNode(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_void_p),
        ('right', ctypes.c_void_p)
    ]

class BalancedTreeCreator:
    def __init__(self):
        self.libc = ctypes.CDLL(None)
        self.malloc = self.libc.malloc
        self.malloc.argtypes = [ctypes.c_size_t]
        self.malloc.restype = ctypes.c_void_p
        
        self.free = self.libc.free
        self.free.argtypes = [ctypes.c_void_p]
    
    def create_perfect_balanced_tree(self, height):
        """Create perfect balanced tree using only memory allocation"""
        if height <= 0:
            return None
        
        # Allocate memory for node
        node_ptr = self.malloc(ctypes.sizeof(TreeNode))
        if not node_ptr:
            return None
        
        # Initialize node structure
        node = TreeNode()
        node.left = self.create_perfect_balanced_tree(height - 1)
        node.right = self.create_perfect_balanced_tree(height - 1)
        
        # Copy structure to allocated memory
        ctypes.memmove(node_ptr, ctypes.byref(node), ctypes.sizeof(TreeNode))
        
        return node_ptr
    
    def traverse_structure(self, root_ptr, depth=0):
        """Traverse tree showing memory structure without storing values"""
        if not root_ptr:
            return
        
        # Cast to TreeNode structure
        node = TreeNode()
        ctypes.memmove(ctypes.byref(node), root_ptr, ctypes.sizeof(TreeNode))
        
        print(f"Depth {depth}: Node at {hex(root_ptr)}")
        print(f"  Left: {hex(node.left) if node.left else 'NULL'}")
        print(f"  Right: {hex(node.right) if node.right else 'NULL'}")
        
        self.traverse_structure(node.left, depth + 1)
        self.traverse_structure(node.right, depth + 1)
    
    def count_nodes(self, root_ptr):
        """Count nodes without storing values"""
        if not root_ptr:
            return 0
        
        node = TreeNode()
        ctypes.memmove(ctypes.byref(node), root_ptr, ctypes.sizeof(TreeNode))
        
        return 1 + self.count_nodes(node.left) + self.count_nodes(node.right)
    
    def free_tree(self, root_ptr):
        """Free allocated memory recursively"""
        if not root_ptr:
            return
        
        node = TreeNode()
        ctypes.memmove(ctypes.byref(node), root_ptr, ctypes.sizeof(TreeNode))
        
        self.free_tree(node.left)
        self.free_tree(node.right)
        self.free(root_ptr)

def main():
    creator = BalancedTreeCreator()
    height = 4  # Creates 2^4 - 1 = 15 nodes
    
    print(f"Creating perfect balanced binary tree with height {height}")
    
    root = creator.create_perfect_balanced_tree(height)
    
    if not root:
        print("Memory allocation failed!")
        return
    
    print("\nTree Structure (memory addresses):")
    creator.traverse_structure(root)
    
    node_count = creator.count_nodes(root)
    expected_nodes = (1 << height) - 1
    
    print(f"\nTotal nodes created: {node_count}")
    print(f"Expected nodes for height {height}: {expected_nodes}")
    
    if node_count == expected_nodes:
        print("✓ Perfect balanced tree verified!")
    else:
        print("✗ Tree structure incorrect!")
    
    creator.free_tree(root)

if __name__ == "__main__":
    main()
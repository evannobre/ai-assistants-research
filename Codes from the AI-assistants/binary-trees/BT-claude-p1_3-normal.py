from collections import deque
import sys

class TreeNode:
    def __init__(self, value, level):
        self.value = value
        self.level = level
        self.left = None
        self.right = None

class BinaryTreeBuilder:
    node_counter = 0
    
    @staticmethod
    def build_perfect_tree(depth):
        if depth < 0:
            return None
        
        BinaryTreeBuilder.node_counter = 0
        root = TreeNode(BinaryTreeBuilder.node_counter, 0)
        BinaryTreeBuilder.node_counter += 1
        
        # Use collections.deque (native, optimized double-ended queue)
        node_queue = deque([root])
        
        while node_queue:
            current = node_queue.popleft()
            
            if current.level < depth:
                # Allocate left child
                current.left = TreeNode(BinaryTreeBuilder.node_counter, current.level + 1)
                BinaryTreeBuilder.node_counter += 1
                node_queue.append(current.left)
                
                # Allocate right child
                current.right = TreeNode(BinaryTreeBuilder.node_counter, current.level + 1)
                BinaryTreeBuilder.node_counter += 1
                node_queue.append(current.right)
        
        return root
    
    @staticmethod
    def print_tree_stats(depth):
        expected_nodes = 2 ** (depth + 1) - 1
        print("Tree Statistics:")
        print(f"Depth: {depth}")
        print(f"Total Nodes Allocated: {BinaryTreeBuilder.node_counter}")
        print(f"Expected Nodes: {expected_nodes}")
    
    @staticmethod
    def get_tree_size(root):
        """Calculate actual memory usage (approximate)"""
        if not root:
            return 0
        return sys.getsizeof(root) + \
               BinaryTreeBuilder.get_tree_size(root.left) + \
               BinaryTreeBuilder.get_tree_size(root.right)

if __name__ == "__main__":
    depth = 10
    
    print(f"Building perfect binary tree of depth {depth}...")
    root = BinaryTreeBuilder.build_perfect_tree(depth)
    
    BinaryTreeBuilder.print_tree_stats(depth)
    
    # Calculate approximate memory usage
    tree_size = BinaryTreeBuilder.get_tree_size(root)
    print(f"\nApproximate memory usage: {tree_size:,} bytes")
    
    print("\nTree built successfully. Root reference held (no GC yet).")
    
    # Verify tree structure
    print(f"Root value: {root.value}")
    print(f"Root left child: {root.left.value if root.left else None}")
    print(f"Root right child: {root.right.value if root.right else None}")
    
    # Delete reference to allow GC
    root = None
    print("\nRoot reference cleared. Python GC will collect when needed.")
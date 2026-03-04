#!/usr/bin/env python3
"""
Perfect Binary Tree with Memory Allocation Management
Author: Computer Scientist specializing in back-end development
Target: Ubuntu 24.04.4 64-bit, 8GB RAM, 256GB SSD

A perfect binary tree of depth N has:
- Total nodes: 2^(N+1) - 1
- Leaf nodes: 2^N
- All internal nodes have exactly 2 children
- All leaves are at the same level
"""

import sys
import gc
import psutil
import os
from typing import Optional, List
from dataclasses import dataclass
import time


@dataclass
class TreeNode:
    """
    Memory-efficient tree node using __slots__ to reduce memory overhead.
    Each node stores only essential data: value and references to children.
    """
    __slots__ = ['value', 'left', 'right']
    
    value: int
    left: Optional['TreeNode']
    right: Optional['TreeNode']
    
    def __init__(self, value: int):
        self.value = value
        self.left = None
        self.right = None


class PerfectBinaryTree:
    """
    Perfect Binary Tree implementation with memory allocation management.
    Uses iterative breadth-first approach to avoid stack overflow for deep trees.
    """
    
    def __init__(self, depth: int):
        """
        Initialize the perfect binary tree builder.
        
        Args:
            depth: The depth of the tree (root is at depth 0)
        """
        self.depth = depth
        self.root: Optional[TreeNode] = None
        self.total_nodes = (2 ** (depth + 1)) - 1
        self.memory_info = {}
        
    def calculate_memory_requirements(self) -> dict:
        """
        Calculate estimated memory requirements for the tree.
        Uses sys.getsizeof for accurate Python object size estimation.
        
        Returns:
            Dictionary with memory statistics
        """
        # Create a sample node to measure actual memory footprint
        sample_node = TreeNode(0)
        node_size = sys.getsizeof(sample_node) + \
                    sys.getsizeof(sample_node.value) + \
                    sys.getsizeof(sample_node.left) + \
                    sys.getsizeof(sample_node.right)
        
        # Add overhead for Python object management
        estimated_size = self.total_nodes * node_size
        
        # Get system memory info
        mem = psutil.virtual_memory()
        
        stats = {
            'total_nodes': self.total_nodes,
            'estimated_bytes': estimated_size,
            'estimated_mb': estimated_size / (1024 * 1024),
            'estimated_gb': estimated_size / (1024 * 1024 * 1024),
            'available_memory_gb': mem.available / (1024 * 1024 * 1024),
            'total_memory_gb': mem.total / (1024 * 1024 * 1024),
            'can_allocate': estimated_size < (mem.available * 0.8)  # Use max 80% of available
        }
        
        self.memory_info = stats
        return stats
    
    def build_iterative(self) -> Optional[TreeNode]:
        """
        Build perfect binary tree iteratively using BFS approach.
        This avoids recursion stack overflow for deep trees.
        Uses native Python collections.deque for efficient queue operations.
        
        Returns:
            Root node of the constructed tree
        """
        from collections import deque
        
        if self.depth < 0:
            return None
        
        # Disable garbage collection during tree construction for performance
        gc.disable()
        
        try:
            # Create root node
            self.root = TreeNode(0)
            node_counter = 1
            
            # Queue stores tuples of (node, current_depth)
            queue: deque = deque([(self.root, 0)])
            
            while queue:
                current_node, current_depth = queue.popleft()
                
                # Only add children if we haven't reached the maximum depth
                if current_depth < self.depth:
                    # Create left child
                    current_node.left = TreeNode(node_counter)
                    queue.append((current_node.left, current_depth + 1))
                    node_counter += 1
                    
                    # Create right child
                    current_node.right = TreeNode(node_counter)
                    queue.append((current_node.right, current_depth + 1))
                    node_counter += 1
            
            return self.root
            
        finally:
            # Re-enable garbage collection
            gc.enable()
    
    def build_recursive(self) -> Optional[TreeNode]:
        """
        Build perfect binary tree recursively.
        More elegant but limited by Python's recursion limit (~1000 by default).
        Only suitable for shallow trees (depth < 10).
        
        Returns:
            Root node of the constructed tree
        """
        gc.disable()
        
        try:
            node_counter = [0]  # Use list to allow mutation in nested function
            
            def create_node(depth: int) -> Optional[TreeNode]:
                if depth > self.depth:
                    return None
                
                node = TreeNode(node_counter[0])
                node_counter[0] += 1
                
                if depth < self.depth:
                    node.left = create_node(depth + 1)
                    node.right = create_node(depth + 1)
                
                return node
            
            self.root = create_node(0)
            return self.root
            
        finally:
            gc.enable()
    
    def verify_perfect_tree(self) -> bool:
        """
        Verify that the constructed tree is indeed a perfect binary tree.
        All leaves should be at the same depth, and all internal nodes should have 2 children.
        
        Returns:
            True if tree is perfect, False otherwise
        """
        if not self.root:
            return self.depth == -1
        
        def get_depth_and_validate(node: Optional[TreeNode]) -> int:
            if node is None:
                return -1
            
            left_depth = get_depth_and_validate(node.left)
            right_depth = get_depth_and_validate(node.right)
            
            # Perfect tree requires left and right subtrees have same depth
            if left_depth != right_depth:
                raise ValueError("Tree is not perfect: unequal subtree depths")
            
            # If node has one child but not the other, it's not perfect
            if (node.left is None) != (node.right is None):
                raise ValueError("Tree is not perfect: node has only one child")
            
            return left_depth + 1
        
        try:
            calculated_depth = get_depth_and_validate(self.root)
            return calculated_depth == self.depth
        except ValueError:
            return False
    
    def count_nodes(self) -> int:
        """
        Count total nodes in the tree (iterative BFS).
        
        Returns:
            Total number of nodes
        """
        if not self.root:
            return 0
        
        from collections import deque
        count = 0
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            count += 1
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        return count
    
    def traverse_inorder(self) -> List[int]:
        """
        Perform iterative in-order traversal (Left-Root-Right).
        Uses native list as stack.
        
        Returns:
            List of node values in in-order sequence
        """
        if not self.root:
            return []
        
        result = []
        stack = []
        current = self.root
        
        while stack or current:
            # Go to leftmost node
            while current:
                stack.append(current)
                current = current.left
            
            # Process node
            current = stack.pop()
            result.append(current.value)
            
            # Move to right subtree
            current = current.right
        
        return result
    
    def get_memory_usage(self) -> dict:
        """
        Get current process memory usage using psutil (native library).
        
        Returns:
            Dictionary with memory usage statistics
        """
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        
        return {
            'rss_mb': mem_info.rss / (1024 * 1024),  # Resident Set Size
            'vms_mb': mem_info.vms / (1024 * 1024),  # Virtual Memory Size
            'percent': process.memory_percent()
        }


def main():
    """
    Main execution function with safety checks and monitoring.
    """
    print("=" * 70)
    print("Perfect Binary Tree Construction with Memory Allocation Management")
    print("=" * 70)
    
    # Get depth from command line or use default
    if len(sys.argv) > 1:
        try:
            depth = int(sys.argv[1])
        except ValueError:
            print("Error: Depth must be an integer")
            sys.exit(1)
    else:
        depth = 10  # Default depth
    
    print(f"\nRequested tree depth: {depth}")
    
    # Create tree builder
    tree = PerfectBinaryTree(depth)
    
    # Calculate and display memory requirements
    print("\n--- Memory Analysis ---")
    mem_stats = tree.calculate_memory_requirements()
    
    print(f"Total nodes to create: {mem_stats['total_nodes']:,}")
    print(f"Estimated memory: {mem_stats['estimated_mb']:.2f} MB "
          f"({mem_stats['estimated_gb']:.4f} GB)")
    print(f"Available memory: {mem_stats['available_memory_gb']:.2f} GB")
    print(f"Total system memory: {mem_stats['total_memory_gb']:.2f} GB")
    
    # Safety check
    if not mem_stats['can_allocate']:
        print("\n❌ ERROR: Insufficient memory to safely allocate this tree!")
        print(f"   Required: {mem_stats['estimated_mb']:.2f} MB")
        print(f"   Available: {mem_stats['available_memory_gb'] * 1024:.2f} MB")
        sys.exit(1)
    
    print("✓ Memory check passed")
    
    # Build the tree
    print("\n--- Building Tree ---")
    initial_mem = tree.get_memory_usage()
    print(f"Initial memory usage: {initial_mem['rss_mb']:.2f} MB")
    
    start_time = time.time()
    
    # Choose build method based on depth
    if depth <= 10:
        print("Using recursive build (suitable for shallow trees)...")
        root = tree.build_recursive()
    else:
        print("Using iterative build (suitable for deep trees)...")
        root = tree.build_iterative()
    
    build_time = time.time() - start_time
    
    final_mem = tree.get_memory_usage()
    print(f"Build completed in {build_time:.4f} seconds")
    print(f"Final memory usage: {final_mem['rss_mb']:.2f} MB")
    print(f"Memory increase: {final_mem['rss_mb'] - initial_mem['rss_mb']:.2f} MB")
    
    # Verify tree structure
    print("\n--- Verification ---")
    node_count = tree.count_nodes()
    is_perfect = tree.verify_perfect_tree()
    
    print(f"Nodes counted: {node_count:,}")
    print(f"Expected nodes: {tree.total_nodes:,}")
    print(f"Tree is perfect: {'✓ Yes' if is_perfect else '✗ No'}")
    
    # Show small traversal sample
    if depth <= 4:  # Only for small trees
        print("\n--- In-order Traversal (sample) ---")
        traversal = tree.traverse_inorder()
        print(f"Values: {traversal}")
    
    # Keep tree in memory - demonstrate it's not GC'd yet
    print("\n--- Memory Retention Test ---")
    print("Tree is still in memory (not garbage collected)")
    print(f"Root node value: {root.value}")
    print(f"Root has left child: {root.left is not None}")
    print(f"Root has right child: {root.right is not None}")
    
    # Force garbage collection and measure
    print("\n--- Garbage Collection Test ---")
    print("Forcing garbage collection...")
    
    # Delete tree references
    tree.root = None
    root = None
    
    # Run GC
    collected = gc.collect()
    time.sleep(0.5)  # Give system time to free memory
    
    gc_mem = tree.get_memory_usage()
    print(f"Objects collected: {collected}")
    print(f"Memory after GC: {gc_mem['rss_mb']:.2f} MB")
    print(f"Memory freed: {final_mem['rss_mb'] - gc_mem['rss_mb']:.2f} MB")
    
    print("\n" + "=" * 70)
    print("Execution completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()

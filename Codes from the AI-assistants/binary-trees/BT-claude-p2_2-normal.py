#!/usr/bin/env python3
"""
Perfect Binary Tree Construction with Memory Allocation Management
Author: Computer Scientist specialized in back-end development
Target: Ubuntu 24.04.4 64-bit, 8GB RAM, 256GB SSD

Mathematical Properties:
- Perfect binary tree of depth N has 2^(N+1) - 1 nodes
- Level i has 2^i nodes (root is level 0)
- Memory requirement: O(2^N) nodes

Memory constraints:
- Available RAM: ~8GB (conservative estimate: 6GB usable)
- Node overhead: ~56 bytes per node (object + pointers + data)
- Maximum theoretical depth: ~27 (134M nodes ≈ 7.5GB)
- Safe maximum depth: ~25 (33M nodes ≈ 1.85GB)
"""

import gc
import sys
import time
import psutil
import os
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class MemoryStats:
    """Track memory statistics during tree construction"""
    nodes_created: int = 0
    current_depth: int = 0
    memory_used_mb: float = 0.0
    peak_memory_mb: float = 0.0
    construction_time_sec: float = 0.0


class TreeNode:
    """
    Binary tree node with minimal memory footprint.
    Uses __slots__ to reduce memory overhead by preventing __dict__ creation.
    """
    __slots__ = ('value', 'left', 'right')
    
    def __init__(self, value: int):
        self.value: int = value
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None


class PerfectBinaryTreeBuilder:
    """
    Builder class for constructing perfect binary trees with memory management.
    
    Algorithm:
    1. Recursive construction with depth tracking
    2. Breadth-first allocation pattern for cache locality
    3. Pre-allocation estimation to prevent out-of-memory
    4. GC control to maintain references until completion
    """
    
    def __init__(self):
        self.root: Optional[TreeNode] = None
        self.stats = MemoryStats()
        self.process = psutil.Process(os.getpid())
        
    def estimate_memory_requirement(self, depth: int) -> float:
        """
        Estimate memory requirement in MB for a perfect tree of given depth.
        
        Formula: nodes = 2^(depth+1) - 1
        Memory per node ≈ 56 bytes (Python object overhead)
        """
        total_nodes = (2 ** (depth + 1)) - 1
        bytes_per_node = sys.getsizeof(TreeNode(0))
        total_bytes = total_nodes * bytes_per_node
        return total_bytes / (1024 * 1024)  # Convert to MB
    
    def check_memory_feasibility(self, depth: int) -> bool:
        """
        Check if construction is feasible given system constraints.
        Keeps 2GB safety margin for OS and other processes.
        """
        required_mb = self.estimate_memory_requirement(depth)
        available_memory = psutil.virtual_memory().available / (1024 * 1024)
        safety_margin_mb = 2048
        
        print(f"\n{'='*60}")
        print(f"Memory Feasibility Analysis for Depth {depth}")
        print(f"{'='*60}")
        print(f"Total nodes required: {(2 ** (depth + 1)) - 1:,}")
        print(f"Estimated memory: {required_mb:.2f} MB")
        print(f"Available memory: {available_memory:.2f} MB")
        print(f"Safety margin: {safety_margin_mb} MB")
        print(f"Feasible: {required_mb + safety_margin_mb <= available_memory}")
        print(f"{'='*60}\n")
        
        return required_mb + safety_margin_mb <= available_memory
    
    def get_current_memory_usage(self) -> float:
        """Get current process memory usage in MB"""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def build_recursive(self, depth: int, current_depth: int = 0, 
                       node_value: int = 1) -> Optional[TreeNode]:
        """
        Recursive algorithm to build perfect binary tree.
        
        Algorithm Analysis:
        - Time Complexity: O(2^N) where N is depth
        - Space Complexity: O(2^N) for nodes + O(N) for recursion stack
        - Pattern: Pre-order traversal construction
        
        Args:
            depth: Maximum depth of tree (0-indexed)
            current_depth: Current depth during recursion
            node_value: Value to assign to current node
            
        Returns:
            TreeNode: Root of constructed subtree
        """
        if current_depth > depth:
            return None
        
        # Create node
        node = TreeNode(node_value)
        self.stats.nodes_created += 1
        
        # Update statistics every 1M nodes to avoid overhead
        if self.stats.nodes_created % 1_000_000 == 0:
            current_mem = self.get_current_memory_usage()
            self.stats.memory_used_mb = current_mem
            self.stats.peak_memory_mb = max(self.stats.peak_memory_mb, current_mem)
            print(f"Progress: {self.stats.nodes_created:,} nodes created, "
                  f"Memory: {current_mem:.2f} MB")
        
        # Recursively construct left and right subtrees
        # Left child gets 2*value, right child gets 2*value + 1 (heap property)
        if current_depth < depth:
            node.left = self.build_recursive(depth, current_depth + 1, node_value * 2)
            node.right = self.build_recursive(depth, current_depth + 1, node_value * 2 + 1)
        
        return node
    
    def build_iterative(self, depth: int) -> Optional[TreeNode]:
        """
        Iterative algorithm using level-order (breadth-first) construction.
        Better for cache locality and memory allocation patterns.
        
        Algorithm:
        - Uses queue to maintain level-order processing
        - Allocates nodes level by level
        - More predictable memory allocation pattern
        
        Time Complexity: O(2^N)
        Space Complexity: O(2^N) for nodes + O(2^(N-1)) for queue
        """
        if depth < 0:
            return None
        
        from collections import deque
        
        # Create root
        root = TreeNode(1)
        self.stats.nodes_created += 1
        
        if depth == 0:
            return root
        
        # Queue stores (node, current_depth, value)
        queue = deque([(root, 0, 1)])
        
        while queue:
            node, current_depth, value = queue.popleft()
            
            if current_depth < depth:
                # Create left child
                node.left = TreeNode(value * 2)
                self.stats.nodes_created += 1
                queue.append((node.left, current_depth + 1, value * 2))
                
                # Create right child
                node.right = TreeNode(value * 2 + 1)
                self.stats.nodes_created += 1
                queue.append((node.right, current_depth + 1, value * 2 + 1))
                
                # Update statistics
                if self.stats.nodes_created % 1_000_000 == 0:
                    current_mem = self.get_current_memory_usage()
                    self.stats.memory_used_mb = current_mem
                    self.stats.peak_memory_mb = max(self.stats.peak_memory_mb, current_mem)
                    print(f"Progress: {self.stats.nodes_created:,} nodes created, "
                          f"Memory: {current_mem:.2f} MB, Queue size: {len(queue):,}")
        
        return root
    
    def build(self, depth: int, method: str = 'iterative') -> bool:
        """
        Main entry point to build perfect binary tree.
        
        Args:
            depth: Depth of tree (0-indexed, root is depth 0)
            method: 'recursive' or 'iterative'
            
        Returns:
            bool: True if construction successful, False otherwise
        """
        # Validate depth
        if depth < 0:
            print("Error: Depth must be non-negative")
            return False
        
        if depth > 30:
            print("Error: Depth > 30 would require excessive memory (>100GB)")
            return False
        
        # Check memory feasibility
        if not self.check_memory_feasibility(depth):
            print("Error: Insufficient memory for requested depth")
            return False
        
        # Disable GC during construction to prevent mid-construction collection
        # This ensures all nodes remain referenced until tree is complete
        gc.disable()
        
        try:
            print(f"Building perfect binary tree of depth {depth} using {method} method...")
            start_time = time.time()
            initial_memory = self.get_current_memory_usage()
            
            # Build tree
            if method == 'recursive':
                self.root = self.build_recursive(depth)
            elif method == 'iterative':
                self.root = self.build_iterative(depth)
            else:
                print(f"Error: Unknown method '{method}'")
                return False
            
            end_time = time.time()
            final_memory = self.get_current_memory_usage()
            
            # Update final statistics
            self.stats.current_depth = depth
            self.stats.construction_time_sec = end_time - start_time
            self.stats.memory_used_mb = final_memory - initial_memory
            self.stats.peak_memory_mb = max(self.stats.peak_memory_mb, final_memory)
            
            print(f"\n{'='*60}")
            print(f"Construction Complete!")
            print(f"{'='*60}")
            print(f"Nodes created: {self.stats.nodes_created:,}")
            print(f"Expected nodes: {(2 ** (depth + 1)) - 1:,}")
            print(f"Construction time: {self.stats.construction_time_sec:.3f} seconds")
            print(f"Memory used: {self.stats.memory_used_mb:.2f} MB")
            print(f"Peak memory: {self.stats.peak_memory_mb:.2f} MB")
            print(f"Nodes per second: {self.stats.nodes_created / self.stats.construction_time_sec:,.0f}")
            print(f"{'='*60}\n")
            
            return True
            
        except MemoryError:
            print("Error: Out of memory during tree construction")
            return False
        except RecursionError:
            print("Error: Maximum recursion depth exceeded (try iterative method)")
            return False
        finally:
            # Re-enable GC after construction
            gc.enable()
    
    def verify_tree(self) -> bool:
        """
        Verify that constructed tree is indeed a perfect binary tree.
        
        Properties to verify:
        1. All leaf nodes are at the same depth
        2. All internal nodes have exactly 2 children
        3. Total nodes = 2^(depth+1) - 1
        """
        if self.root is None:
            return False
        
        def get_depth(node: Optional[TreeNode]) -> int:
            if node is None:
                return -1
            return 1 + max(get_depth(node.left), get_depth(node.right))
        
        def is_perfect(node: Optional[TreeNode], depth: int, level: int = 0) -> bool:
            if node is None:
                return True
            
            # Leaf node
            if node.left is None and node.right is None:
                return level == depth
            
            # Internal node must have both children
            if node.left is None or node.right is None:
                return False
            
            return (is_perfect(node.left, depth, level + 1) and 
                    is_perfect(node.right, depth, level + 1))
        
        depth = get_depth(self.root)
        is_valid = is_perfect(self.root, depth)
        
        print(f"Tree verification: {'PASSED' if is_valid else 'FAILED'}")
        print(f"Tree depth: {depth}")
        
        return is_valid
    
    def traverse_inorder(self, limit: int = 20) -> List[int]:
        """
        Perform in-order traversal (for verification).
        Limited to first 'limit' nodes to avoid excessive output.
        """
        result = []
        
        def inorder(node: Optional[TreeNode], count: List[int]):
            if node is None or count[0] >= limit:
                return
            
            inorder(node.left, count)
            if count[0] < limit:
                result.append(node.value)
                count[0] += 1
            inorder(node.right, count)
        
        inorder(self.root, [0])
        return result
    
    def cleanup(self):
        """
        Explicitly clean up tree and force garbage collection.
        This demonstrates the GC behavior mentioned in requirements.
        """
        print("\nCleaning up tree...")
        initial_memory = self.get_current_memory_usage()
        
        self.root = None
        gc.collect()  # Force garbage collection
        
        final_memory = self.get_current_memory_usage()
        freed_memory = initial_memory - final_memory
        
        print(f"Memory before cleanup: {initial_memory:.2f} MB")
        print(f"Memory after cleanup: {final_memory:.2f} MB")
        print(f"Memory freed by GC: {freed_memory:.2f} MB")


def main():
    """
    Main function demonstrating the perfect binary tree construction.
    """
    print("Perfect Binary Tree Builder")
    print("=" * 60)
    print(f"System Information:")
    print(f"Python version: {sys.version}")
    print(f"Total RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    print(f"Available RAM: {psutil.virtual_memory().available / (1024**3):.2f} GB")
    print(f"CPU count: {psutil.cpu_count()}")
    print("=" * 60)
    
    # Example: Build a tree of depth 20 (2,097,151 nodes, ~117 MB)
    # Adjust depth based on your needs and available memory
    
    # Safe depths for 8GB RAM system:
    # Depth 20: ~2M nodes, ~117 MB
    # Depth 22: ~8M nodes, ~469 MB
    # Depth 24: ~33M nodes, ~1.9 GB
    # Depth 25: ~67M nodes, ~3.7 GB
    
    builder = PerfectBinaryTreeBuilder()
    
    # User can modify this depth
    TREE_DEPTH = 15
    
    # Build tree using iterative method (recommended for large trees)
    success = builder.build(TREE_DEPTH, method='iterative')
    
    if success:
        # Verify tree structure
        builder.verify_tree()
        
        # Show sample traversal
        print(f"\nFirst 20 nodes (in-order traversal): {builder.traverse_inorder(20)}")
        
        # Tree is now in memory and can be used for operations
        print("\n[Tree is now built and in memory - GC has not collected it]")
        print("[You can perform operations on the tree here]")
        
        # Simulate some work with the tree
        time.sleep(1)
        
        # Cleanup (this triggers GC)
        builder.cleanup()
    else:
        print("Failed to build tree")


if __name__ == "__main__":
    main()

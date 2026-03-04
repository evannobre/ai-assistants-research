#!/usr/bin/env python3
"""
Perfect Binary Tree Memory Allocation Simulator
Creates a perfect binary tree of depth N and tracks memory allocation
before garbage collection occurs.
"""

import sys
import gc
import tracemalloc
from dataclasses import dataclass
from typing import Optional


@dataclass
class TreeNode:
    """Node in a binary tree with value and children."""
    value: int
    left: Optional['TreeNode'] = None
    right: Optional['TreeNode'] = None
    
    def __sizeof__(self):
        """Calculate the size of this node."""
        # Base object size plus references
        return object.__sizeof__(self) + sys.getsizeof(self.value)


class PerfectBinaryTreeAllocator:
    """
    Allocates and manages a perfect binary tree with memory tracking.
    A perfect binary tree has all leaf nodes at the same depth and
    all internal nodes have exactly 2 children.
    """
    
    def __init__(self, depth: int):
        """
        Initialize the allocator with target depth.
        
        Args:
            depth: Depth of the perfect binary tree (root is depth 0)
        """
        self.depth = depth
        self.root = None
        self.node_count = 0
        self.total_nodes = (2 ** (depth + 1)) - 1  # Formula for perfect binary tree
        
    def allocate_tree(self) -> TreeNode:
        """
        Main algorithm to allocate a perfect binary tree.
        
        Returns:
            Root node of the created tree
        """
        print(f"\n{'='*60}")
        print(f"Allocating Perfect Binary Tree - Depth: {self.depth}")
        print(f"Expected nodes: {self.total_nodes}")
        print(f"{'='*60}\n")
        
        # Disable garbage collection to prevent premature cleanup
        gc.disable()
        
        # Start memory tracking
        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()
        
        # Allocate the tree
        self.root = self._allocate_recursive(0, 0)
        
        # Take snapshot after allocation
        snapshot_after = tracemalloc.take_snapshot()
        
        # Calculate memory statistics
        self._print_memory_stats(snapshot_before, snapshot_after)
        
        # Verify tree structure
        self._verify_tree()
        
        return self.root
    
    def _allocate_recursive(self, current_depth: int, node_value: int) -> Optional[TreeNode]:
        """
        Recursively allocate nodes for the perfect binary tree.
        
        Algorithm:
        1. Base case: if current_depth > target_depth, return None
        2. Allocate new node with current value
        3. Recursively allocate left subtree (depth + 1)
        4. Recursively allocate right subtree (depth + 1)
        5. Return the allocated node
        
        Args:
            current_depth: Current depth in the tree
            node_value: Value to assign to this node
            
        Returns:
            Allocated TreeNode or None if beyond depth limit
        """
        if current_depth > self.depth:
            return None
        
        # Allocate new node
        node = TreeNode(value=node_value)
        self.node_count += 1
        
        # Calculate child values for binary heap-like indexing
        left_value = 2 * node_value + 1
        right_value = 2 * node_value + 2
        
        # Recursively allocate children
        node.left = self._allocate_recursive(current_depth + 1, left_value)
        node.right = self._allocate_recursive(current_depth + 1, right_value)
        
        return node
    
    def _verify_tree(self):
        """Verify the tree structure is correct."""
        print(f"\nTree Verification:")
        print(f"  Nodes allocated: {self.node_count}")
        print(f"  Expected nodes: {self.total_nodes}")
        print(f"  Status: {'✓ PASS' if self.node_count == self.total_nodes else '✗ FAIL'}")
        
        # Verify depth
        actual_depth = self._calculate_depth(self.root)
        print(f"  Actual depth: {actual_depth}")
        print(f"  Expected depth: {self.depth}")
        print(f"  Depth check: {'✓ PASS' if actual_depth == self.depth else '✗ FAIL'}")
    
    def _calculate_depth(self, node: Optional[TreeNode], current_depth: int = 0) -> int:
        """Calculate the maximum depth of the tree."""
        if node is None:
            return current_depth - 1
        
        left_depth = self._calculate_depth(node.left, current_depth + 1)
        right_depth = self._calculate_depth(node.right, current_depth + 1)
        
        return max(left_depth, right_depth)
    
    def _print_memory_stats(self, snapshot_before, snapshot_after):
        """Print memory allocation statistics."""
        print("\nMemory Allocation Statistics:")
        print(f"{'='*60}")
        
        # Compare snapshots
        top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
        
        total_allocated = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
        
        print(f"  Total memory allocated: {total_allocated:,} bytes")
        print(f"  Memory per node (avg): {total_allocated / self.node_count:.2f} bytes")
        print(f"  Total nodes: {self.node_count}")
        
        print(f"\n  Top memory allocations:")
        for stat in top_stats[:5]:
            if stat.size_diff > 0:
                print(f"    {stat.size_diff:>10,} bytes - {stat.traceback.format()[0]}")
        
        # Current memory usage
        current, peak = tracemalloc.get_traced_memory()
        print(f"\n  Current memory: {current:,} bytes")
        print(f"  Peak memory: {peak:,} bytes")
        
        tracemalloc.stop()
    
    def traverse_preorder(self, node: Optional[TreeNode] = None, depth: int = 0, max_display: int = 20):
        """
        Traverse and display tree in preorder (limited output).
        
        Args:
            node: Current node (uses root if None)
            depth: Current depth for indentation
            max_display: Maximum nodes to display
        """
        if node is None:
            node = self.root
        
        if self.node_count > max_display and depth > 2:
            return
        
        indent = "  " * depth
        print(f"{indent}Node(value={node.value}, depth={depth})")
        
        if node.left:
            self.traverse_preorder(node.left, depth + 1, max_display)
        if node.right:
            self.traverse_preorder(node.right, depth + 1, max_display)
    
    def cleanup(self):
        """Clean up the tree and re-enable garbage collection."""
        print(f"\n{'='*60}")
        print("Cleanup Phase")
        print(f"{'='*60}")
        
        # Show memory before cleanup
        current_before = sys.getsizeof(self.root)
        print(f"  Memory before cleanup (root only): {current_before:,} bytes")
        
        # Clear the tree
        self.root = None
        self.node_count = 0
        
        # Re-enable garbage collection
        gc.enable()
        collected = gc.collect()
        
        print(f"  Garbage collection re-enabled")
        print(f"  Objects collected: {collected}")
        print(f"  Tree cleared: ✓")


def main():
    """Main execution function."""
    # Test with different depths
    depths = [3, 5, 8]
    
    for depth in depths:
        print(f"\n{'#'*60}")
        print(f"# Testing with Depth = {depth}")
        print(f"{'#'*60}")
        
        allocator = PerfectBinaryTreeAllocator(depth)
        
        # Allocate tree (GC is disabled during this)
        root = allocator.allocate_tree()
        
        # Display tree structure (limited)
        if depth <= 4:
            print(f"\nTree Structure (Preorder Traversal):")
            print(f"{'='*60}")
            allocator.traverse_preorder()
        
        # Keep reference alive - tree is still in memory before GC
        print(f"\n⚠️  Tree is in memory, GC is DISABLED")
        print(f"   All {allocator.node_count} nodes are allocated and accessible")
        
        # Cleanup and trigger GC
        allocator.cleanup()
        
        print(f"\n✓ Test completed for depth {depth}\n")


if __name__ == "__main__":
    print("Perfect Binary Tree Memory Allocator")
    print("=" * 60)
    main()

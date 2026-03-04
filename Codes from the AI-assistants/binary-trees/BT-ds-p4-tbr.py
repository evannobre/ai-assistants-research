#!/usr/bin/env python3
"""
Binary Trees Benchmark Implementation
Based on the requirements for creating perfect binary trees with specific memory patterns
Uses Python's native garbage collection and memory allocation patterns
"""

import sys
import gc
import time
from typing import Optional, Tuple

class TreeNode:
    """Tree node class with reference counting for tracking allocations"""
    __slots__ = ('left', 'right', 'value')
    
    allocation_count = 0
    live_count = 0
    
    def __init__(self, left: Optional['TreeNode'], right: Optional['TreeNode'], value: int = 0):
        self.left = left
        self.right = right
        self.value = value
        TreeNode.allocation_count += 1
        TreeNode.live_count += 1
    
    def __del__(self):
        TreeNode.live_count -= 1
    
    @staticmethod
    def create_bottom_up(depth: int) -> Optional['TreeNode']:
        """Create a perfect binary tree bottom-up"""
        if depth <= 0:
            return TreeNode(None, None, 1)
        return TreeNode(
            TreeNode.create_bottom_up(depth - 1),
            TreeNode.create_bottom_up(depth - 1),
            1
        )
    
    def count_nodes(self) -> int:
        """Count nodes in the tree"""
        if self.left is None and self.right is None:
            return 1
        count = 1
        if self.left:
            count += self.left.count_nodes()
        if self.right:
            count += self.right.count_nodes()
        return count
    
    def cleanup(self) -> None:
        """Explicitly clean up tree nodes by breaking cycles"""
        if self.left:
            self.left.cleanup()
            self.left = None
        if self.right:
            self.right.cleanup()
            self.right = None

class TreeAllocator:
    """Manages tree allocations and deallocations"""
    
    def __init__(self, max_depth: int):
        self.max_depth = max_depth
        self.min_depth = 4
        self.long_lived_tree: Optional[TreeNode] = None
        
    def allocate_stretch_tree(self) -> Tuple[Optional[TreeNode], int]:
        """Allocate a stretch tree that will be immediately deallocated"""
        stretch_depth = self.max_depth + 1
        tree = TreeNode.create_bottom_up(stretch_depth)
        if tree is None:
            raise MemoryError(f"Failed to allocate stretch tree of depth {stretch_depth}")
        
        node_count = tree.count_nodes()
        expected = 2 ** (stretch_depth + 1) - 1
        
        if node_count != expected:
            raise ValueError(f"Stretch tree node count mismatch: {node_count} != {expected}")
        
        print(f"stretch tree of depth {stretch_depth}\t check: {node_count}")
        return tree, node_count
    
    def allocate_long_lived_tree(self) -> None:
        """Allocate the long-lived tree that persists through benchmark"""
        self.long_lived_tree = TreeNode.create_bottom_up(self.max_depth)
        if self.long_lived_tree is None:
            raise MemoryError(f"Failed to allocate long-lived tree of depth {self.max_depth}")
        
        node_count = self.long_lived_tree.count_nodes()
        expected = 2 ** (self.max_depth + 1) - 1
        
        if node_count != expected:
            raise ValueError(f"Long-lived tree node count mismatch: {node_count} != {expected}")
    
    def process_depth(self, depth: int) -> int:
        """Process trees of a specific depth"""
        iterations = 2 ** (self.max_depth - depth + self.min_depth)
        total_nodes = 0
        
        for _ in range(iterations):
            # Allocate tree
            tree = TreeNode.create_bottom_up(depth)
            if tree is None:
                raise MemoryError(f"Failed to allocate tree of depth {depth}")
            
            # Walk and count nodes
            node_count = tree.count_nodes()
            expected = 2 ** (depth + 1) - 1
            
            if node_count != expected:
                raise ValueError(f"Tree node count mismatch: {node_count} != {expected}")
            
            total_nodes += node_count
            
            # Deallocate tree
            tree.cleanup()
            tree = None
        
        print(f"{iterations}\t trees of depth {depth}\t check: {total_nodes}")
        return total_nodes
    
    def verify_long_lived_tree(self) -> bool:
        """Verify the long-lived tree still exists"""
        if self.long_lived_tree is None:
            return False
        
        node_count = self.long_lived_tree.count_nodes()
        expected = 2 ** (self.max_depth + 1) - 1
        
        if node_count != expected:
            raise ValueError(f"Long-lived tree verification failed: {node_count} != {expected}")
        
        print(f"long lived tree of depth {self.max_depth}\t check: {node_count}")
        return True

def run_benchmark(max_depth: int) -> None:
    """Main benchmark function"""
    print(f"Running binary trees benchmark with max depth {max_depth}")
    print("=" * 60)
    
    # Disable GC during allocations for more predictable behavior
    gc.disable()
    
    allocator = TreeAllocator(max_depth)
    
    # 1. Stretch tree allocation and deallocation
    print("\n1. Allocating and deallocating stretch tree...")
    stretch_tree, stretch_nodes = allocator.allocate_stretch_tree()
    
    # Force deallocation
    stretch_tree.cleanup()
    stretch_tree = None
    
    # Force garbage collection
    gc.collect()
    
    # 2. Allocate long-lived tree
    print("\n2. Allocating long-lived tree...")
    allocator.allocate_long_lived_tree()
    
    # 3. Process trees of various depths
    print("\n3. Processing trees of various depths...")
    start_time = time.time()
    
    total_processed_nodes = 0
    for depth in range(allocator.min_depth, max_depth + 1, 2):
        total_processed_nodes += allocator.process_depth(depth)
    
    elapsed = time.time() - start_time
    print(f"\nTotal processed nodes: {total_processed_nodes:,}")
    print(f"Processing time: {elapsed:.2f} seconds")
    print(f"Nodes per second: {total_processed_nodes / elapsed:,.0f}")
    
    # 4. Verify long-lived tree
    print("\n4. Verifying long-lived tree...")
    if allocator.verify_long_lived_tree():
        print("✓ Long-lived tree verified successfully")
    else:
        print("✗ Long-lived tree verification failed")
    
    # Memory statistics
    print("\n" + "=" * 60)
    print("Memory Statistics:")
    print(f"Total allocations: {TreeNode.allocation_count:,}")
    print(f"Current live nodes: {TreeNode.live_count:,}")
    
    # Enable GC again
    gc.enable()
    
    # Final cleanup
    if allocator.long_lived_tree:
        allocator.long_lived_tree.cleanup()
        allocator.long_lived_tree = None
    
    gc.collect()
    
    print("\n✓ Benchmark completed successfully")

def memory_safety_check(max_depth: int) -> bool:
    """Check if the system has enough memory for the benchmark"""
    import psutil
    
    # Estimate memory needed for one tree
    # Each TreeNode: ~56 bytes overhead + 2*8 bytes for pointers + 8 bytes for value
    # ~80 bytes per node
    nodes_per_tree = 2 ** (max_depth + 2) - 1  # Worst case: stretch tree
    memory_per_tree = nodes_per_tree * 80  # bytes
    
    # Convert to MB
    memory_per_tree_mb = memory_per_tree / (1024 * 1024)
    
    # Get available memory
    available_memory = psutil.virtual_memory().available / (1024 * 1024)
    
    print(f"Memory estimation for depth {max_depth}:")
    print(f"  Nodes per tree (max): {nodes_per_tree:,}")
    print(f"  Estimated memory per tree: {memory_per_tree_mb:.2f} MB")
    print(f"  Available memory: {available_memory:.2f} MB")
    
    # Need at least 3x the tree size (stretch + long-lived + one in process)
    required_memory = memory_per_tree_mb * 3
    
    if required_memory > available_memory * 0.8:  # Use 80% of available as safety margin
        print(f"\n⚠ Warning: Memory requirements ({required_memory:.2f} MB) may exceed available memory")
        return False
    
    return True

def main():
    """Main entry point"""
    # Parse command line argument
    if len(sys.argv) > 1:
        try:
            max_depth = int(sys.argv[1])
        except ValueError:
            print(f"Invalid depth argument: {sys.argv[1]}")
            print("Usage: python binary_trees.py [depth]")
            sys.exit(1)
    else:
        max_depth = 21  # Default
    
    print(f"Binary Trees Benchmark")
    print(f"System: Ubuntu 24.04.4 64-bit")
    print(f"Configuration: SSD 256 GB, RAM 8 GB")
    print(f"Requested depth: {max_depth}")
    
    # Safety check
    if max_depth > 24:
        print(f"\n⚠ Warning: Depth {max_depth} may cause memory issues on 8GB RAM")
        print("Consider using a lower depth (21 is recommended)")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Benchmark cancelled")
            sys.exit(0)
    
    try:
        # Run memory safety check
        if not memory_safety_check(max_depth):
            print("\n⚠ Memory safety check failed")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Benchmark cancelled")
                sys.exit(0)
        
        # Run benchmark
        run_benchmark(max_depth)
        
    except MemoryError as e:
        print(f"\n✗ Memory error: {e}")
        print("The benchmark requires more memory than available.")
        print("Try running with a lower depth value.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error during benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
import sys
import gc
import time
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class TreeNode:
    """Tree node class - same structure for both interior and leaf nodes"""
    left: Optional['TreeNode']
    right: Optional['TreeNode']
    # Add some payload to prevent optimization
    value: int = 0
    
    def __post_init__(self):
        # Add a computation to ensure work isn't optimized away
        self.value = id(self) % 1000

def create_perfect_binary_tree(depth: int) -> Optional[TreeNode]:
    """Create a perfect binary tree of given depth"""
    if depth <= 0:
        return None
    
    # Create nodes bottom-up
    if depth == 1:
        # Leaf node - same structure as interior nodes
        return TreeNode(None, None)
    else:
        left = create_perfect_binary_tree(depth - 1)
        right = create_perfect_binary_tree(depth - 1)
        return TreeNode(left, right)

def walk_tree(node: Optional[TreeNode]) -> int:
    """Walk tree and count nodes"""
    if node is None:
        return 0
    
    # Do some minimal computation with node value
    count = 1
    count += walk_tree(node.left)
    count += walk_tree(node.right)
    
    # Add some work to prevent optimization
    return count + (node.value % 2)

def check_tree_exists(node: Optional[TreeNode], expected_count: int) -> bool:
    """Verify tree exists and has correct number of nodes"""
    if node is None:
        return expected_count == 0
    
    actual_count = walk_tree(node)
    return actual_count == expected_count

def benchmark(stretch_depth: int, long_lived_depth: int, iterations: int):
    """Main benchmark function"""
    print(f"Stretch tree of depth {stretch_depth}")
    print(f"Long-lived tree of depth {long_lived_depth}")
    print(f"Creating {iterations} trees of depth {iterations}")
    
    # 1. Create stretch tree (short-lived)
    stretch_tree = create_perfect_binary_tree(stretch_depth)
    stretch_count = walk_tree(stretch_tree)
    print(f"  stretch tree count: {stretch_count}")
    
    # Explicitly delete and force GC to show we're doing work
    del stretch_tree
    if 'pypy' not in sys.implementation.name:  # PyPy handles this differently
        gc.collect()
    
    # 2. Create long-lived tree
    print("Creating long-lived tree...")
    long_lived_tree = create_perfect_binary_tree(long_lived_depth)
    long_lived_count = walk_tree(long_lived_tree)
    print(f"  long-lived tree count: {long_lived_count}")
    
    # 3. Create many bottom-up trees
    print("Creating many bottom-up trees...")
    start_time = time.time()
    
    total_count = 0
    for i in range(iterations):
        # Create tree of depth based on iteration
        depth = iterations
        if i % 2 == 0:
            depth -= 1
        
        # Create, walk, and delete tree
        tree = create_perfect_binary_tree(depth)
        count = walk_tree(tree)
        total_count += count
        
        # Delete tree to allow GC
        del tree
        
        # Periodically collect garbage
        if i % 10 == 0 and 'pypy' not in sys.implementation.name:
            gc.collect()
    
    end_time = time.time()
    
    print(f"Total nodes created: {total_count}")
    print(f"Time elapsed: {end_time - start_time:.3f} seconds")
    
    # 4. Verify long-lived tree still exists
    if check_tree_exists(long_lived_tree, long_lived_count):
        print("Long-lived tree verified successfully")
    else:
        print("ERROR: Long-lived tree corrupted!")
    
    # Final cleanup
    del long_lived_tree
    if 'pypy' not in sys.implementation.name:
        gc.collect()

def main():
    # Parse command line argument
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} <depth>")
            print("Using default depth: 21")
            n = 21
    else:
        print("Using default depth: 21")
        n = 21
    
    # Minimum 4 allocations as specified
    stretch_depth = n + 1
    long_lived_depth = n
    iterations = max(4, 2 ** (n - 4))  # Ensure at least 4 iterations
    
    print(f"Binary Tree Benchmark (Python {sys.version.split()[0]})")
    print(f"Running with depth={n}")
    print(f"Minimum allocations: {iterations}")
    print("-" * 50)
    
    # Disable GC during benchmark for more consistent timing
    # (but we'll manually collect periodically)
    gc_was_enabled = gc.isenabled()
    if 'pypy' not in sys.implementation.name:
        gc.disable()
    
    try:
        benchmark(stretch_depth, long_lived_depth, iterations)
    finally:
        # Restore GC state
        if gc_was_enabled and 'pypy' not in sys.implementation.name:
            gc.enable()
    
    print("-" * 50)
    print("Benchmark complete")

if __name__ == "__main__":
    # Ensure we're using Python's native GC
    print(f"Python implementation: {sys.implementation.name}")
    print(f"GC enabled: {gc.isenabled()}")
    
    # Force full collection before starting
    if 'pypy' not in sys.implementation.name:
        gc.collect()
    
    main()
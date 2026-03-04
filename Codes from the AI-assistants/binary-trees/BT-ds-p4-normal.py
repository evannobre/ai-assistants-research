import sys
import gc
import time
from typing import Optional, ClassVar

class TreeNode:
    """Tree node class for perfect binary trees."""
    # Class variable to track allocations for verification
    allocation_count: ClassVar[int] = 0
    node_id: ClassVar[int] = 0
    
    def __init__(self, left: Optional['TreeNode'] = None, 
                 right: Optional['TreeNode'] = None):
        self.left = left
        self.right = right
        self.id = TreeNode.node_id
        TreeNode.node_id += 1
        TreeNode.allocation_count += 1
    
    def __repr__(self) -> str:
        return f"TreeNode(id={self.id})"

def create_perfect_binary_tree(depth: int) -> Optional[TreeNode]:
    """Create a perfect binary tree of given depth using recursive bottom-up allocation."""
    if depth <= 0:
        return None
    
    # Create left and right subtrees recursively
    left = create_perfect_binary_tree(depth - 1)
    right = create_perfect_binary_tree(depth - 1)
    
    # Create node with subtrees (allocation happens here)
    return TreeNode(left, right)

def count_nodes(tree: Optional[TreeNode]) -> int:
    """Count nodes in the tree using depth-first traversal."""
    if tree is None:
        return 0
    return 1 + count_nodes(tree.left) + count_nodes(tree.right)

def walk_tree(tree: Optional[TreeNode]) -> int:
    """Walk the tree and return node count. Also verifies structure."""
    if tree is None:
        return 0
    
    # Simple depth-first traversal
    count = 1
    
    if tree.left is not None:
        count += walk_tree(tree.left)
    if tree.right is not None:
        count += walk_tree(tree.right)
    
    return count

def deallocate_tree(tree: Optional[TreeNode]):
    """Explicitly break circular references to help GC."""
    if tree is None:
        return
    
    # Recursively break references
    deallocate_tree(tree.left)
    deallocate_tree(tree.right)
    
    # Clear references
    tree.left = None
    tree.right = None

def verify_tree_exists(tree: Optional[TreeNode], expected_nodes: int) -> bool:
    """Verify that a tree exists and has the expected number of nodes."""
    if tree is None:
        return False
    
    actual_nodes = walk_tree(tree)
    return actual_nodes == expected_nodes

def main():
    # Parse command line argument
    if len(sys.argv) > 1:
        try:
            max_depth = max(int(sys.argv[1]), 4)
        except ValueError:
            max_depth = 21
    else:
        max_depth = 21
    
    # Adjust for memory constraints (8GB RAM)
    # Each TreeNode in Python is ~56 bytes, plus overhead
    # For depth=21, nodes = 2^(21+1)-1 = ~4.2 million nodes
    # Memory required: ~4.2M * 56 bytes = ~235MB
    # This is within 8GB constraints
    if max_depth > 22:
        print(f"Warning: Depth {max_depth} might exceed memory constraints on 8GB system")
        print("Reducing to depth 22 for safety")
        max_depth = 22
    
    stretch_depth = max_depth + 1
    long_lived_depth = max_depth
    
    print(f"Running with max depth: {max_depth}")
    print(f"Stretch tree depth: {stretch_depth}")
    print(f"Long-lived tree depth: {long_lived_depth}")
    
    # Get initial allocation count
    initial_count = TreeNode.allocation_count
    
    # 1. Allocate stretch tree (check memory)
    print("\n1. Allocating stretch tree...")
    stretch_tree = create_perfect_binary_tree(stretch_depth)
    stretch_nodes = (1 << (stretch_depth + 1)) - 1
    actual_stretch_nodes = walk_tree(stretch_tree)
    
    print(f"Stretch tree created. Expected nodes: {stretch_nodes}, Actual: {actual_stretch_nodes}")
    
    if stretch_nodes != actual_stretch_nodes:
        print(f"ERROR: Stretch tree node count mismatch!")
        return 1
    
    # Verify it exists
    print("Verifying stretch tree exists...")
    if verify_tree_exists(stretch_tree, stretch_nodes):
        print("✓ Stretch tree verification passed")
    else:
        print("✗ Stretch tree verification failed")
        return 1
    
    # Deallocate stretch tree
    print("Deallocating stretch tree...")
    deallocate_tree(stretch_tree)
    stretch_tree = None
    
    # Force garbage collection
    gc.collect()
    
    # 2. Create long-lived tree
    print("\n2. Creating long-lived tree...")
    long_lived_tree = create_perfect_binary_tree(long_lived_depth)
    long_lived_nodes = (1 << (long_lived_depth + 1)) - 1
    actual_long_lived_nodes = walk_tree(long_lived_tree)
    
    print(f"Long-lived tree created. Expected nodes: {long_lived_nodes}, Actual: {actual_long_lived_nodes}")
    
    if long_lived_nodes != actual_long_lived_nodes:
        print(f"ERROR: Long-lived tree node count mismatch!")
        return 1
    
    # 3. Allocate, walk, and deallocate many bottom-up trees
    print("\n3. Processing bottom-up trees...")
    
    min_depth = 4
    max_iterations = max_depth - min_depth + 1
    
    start_time = time.time()
    
    for depth in range(min_depth, max_depth + 1):
        iterations = 1 << (max_depth - depth + min_depth)
        
        print(f"\nDepth {depth}: {iterations} iterations")
        
        total_nodes_created = 0
        total_nodes_walked = 0
        
        for i in range(iterations):
            # Allocate tree
            tree = create_perfect_binary_tree(depth)
            expected_nodes = (1 << (depth + 1)) - 1
            
            # Walk tree (count nodes)
            node_count = walk_tree(tree)
            total_nodes_walked += node_count
            
            # Verify
            if node_count != expected_nodes:
                print(f"ERROR: Iteration {i+1}/{iterations}: Expected {expected_nodes}, got {node_count}")
                return 1
            
            # Deallocate
            deallocate_tree(tree)
            tree = None
            
            # Periodically force GC to prevent memory buildup
            if i > 0 and i % 100 == 0:
                gc.collect()
        
        print(f"  Created and walked {total_nodes_walked} total nodes")
    
    elapsed_time = time.time() - start_time
    print(f"\nBottom-up trees processing completed in {elapsed_time:.2f} seconds")
    
    # 4. Verify long-lived tree still exists
    print("\n4. Verifying long-lived tree still exists...")
    if verify_tree_exists(long_lived_tree, long_lived_nodes):
        print("✓ Long-lived tree verification passed")
    else:
        print("✗ Long-lived tree verification failed")
        return 1
    
    # Final statistics
    print("\n" + "="*50)
    print("FINAL STATISTICS:")
    print(f"Total TreeNode allocations: {TreeNode.allocation_count - initial_count}")
    print(f"Stretch tree depth: {stretch_depth}")
    print(f"Long-lived tree depth: {long_lived_depth}")
    print(f"Long-lived tree nodes: {long_lived_nodes}")
    print("="*50)
    
    # Final cleanup
    print("\nPerforming final cleanup...")
    deallocate_tree(long_lived_tree)
    long_lived_tree = None
    gc.collect()
    
    print("\n✓ Program completed successfully")
    return 0

if __name__ == "__main__":
    # Disable automatic garbage collection during tree operations
    # for more predictable behavior, but run it manually
    gc.disable()
    
    exit_code = main()
    
    # Re-enable GC
    gc.enable()
    
    # Final GC
    collected = gc.collect()
    print(f"Final garbage collection: {collected} objects collected")
    
    sys.exit(exit_code)
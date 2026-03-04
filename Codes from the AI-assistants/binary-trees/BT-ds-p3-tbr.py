import sys
import gc

class TreeNode:
    """Tree node class with left and right children"""
    __slots__ = ('left', 'right')
    
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right


def create_bottom_up_tree(depth):
    """Create a perfect binary tree bottom-up (from leaves to root)"""
    if depth <= 0:
        return TreeNode()
    return TreeNode(
        create_bottom_up_tree(depth - 1),
        create_bottom_up_tree(depth - 1)
    )


def walk_tree_count_nodes(node):
    """Walk the tree and count all nodes"""
    count = 1  # Count current node
    if node.left:
        count += walk_tree_count_nodes(node.left)
    if node.right:
        count += walk_tree_count_nodes(node.right)
    return count


def benchmark(depth):
    """Run the binary tree benchmark with specified depth"""
    print(f"Running binary tree benchmark with depth {depth}")
    
    # 1. Stretch tree - allocate, check, and immediately deallocate
    print("\n1. Creating and checking stretch tree (depth + 1)...")
    stretch_tree = create_bottom_up_tree(depth + 1)
    stretch_count = walk_tree_count_nodes(stretch_tree)
    print(f"   Stretch tree node count: {stretch_count}")
    print(f"   Expected: {2**(depth + 2) - 1}")
    # Deallocate by letting it go out of scope
    stretch_tree = None
    
    # Force garbage collection to simulate "before any GC" as much as possible
    # (though we can't fully prevent GC in Python)
    gc.collect()
    
    # 2. Long-lived tree
    print("\n2. Creating long-lived tree...")
    long_lived_tree = create_bottom_up_tree(depth)
    long_lived_count = walk_tree_count_nodes(long_lived_tree)
    print(f"   Long-lived tree node count: {long_lived_count}")
    print(f"   Expected: {2**(depth + 1) - 1}")
    
    # 3. Allocate, walk, and deallocate many trees
    print("\n3. Creating and destroying many trees...")
    total_nodes_allocated = 0
    iterations = 4  # Minimum 4 allocations as specified
    
    for i in range(iterations):
        # Alternate depths to vary allocation patterns
        current_depth = depth - (i % 2)
        tree = create_bottom_up_tree(current_depth)
        node_count = walk_tree_count_nodes(tree)
        total_nodes_allocated += node_count
        
        # Deallocate by letting it go out of scope
        tree = None
        
        # Optional: Force GC every few iterations to be explicit about deallocation
        if i % 2 == 0:
            gc.collect()
        
        print(f"   Tree {i+1}: depth {current_depth}, nodes {node_count}")
    
    # 4. Verify long-lived tree still exists
    print("\n4. Verifying long-lived tree still exists...")
    final_count = walk_tree_count_nodes(long_lived_tree)
    if final_count == long_lived_count:
        print(f"   ✓ Long-lived tree intact with {final_count} nodes")
    else:
        print(f"   ✗ Long-lived tree corrupted! Expected {long_lived_count}, got {final_count}")
    
    print(f"\nTotal nodes allocated across all trees: {total_nodes_allocated}")
    
    # Clean up
    long_lived_tree = None
    gc.collect()
    
    return True


def main():
    # Use command line argument or default to 21
    try:
        depth = int(sys.argv[1]) if len(sys.argv) > 1 else 21
    except ValueError:
        print(f"Invalid depth argument: {sys.argv[1]}. Using default depth 21.")
        depth = 21
    
    if depth < 1:
        print("Depth must be at least 1. Using depth 1.")
        depth = 1
    
    # Disable automatic garbage collection during the benchmark
    # to better match "before any GC" requirement
    gc.disable()
    
    try:
        success = benchmark(depth)
        
        if success:
            print(f"\n✓ Benchmark completed successfully with depth {depth}")
            print(f"Tree statistics:")
            print(f"  - Stretch tree depth: {depth + 1}")
            print(f"  - Long-lived tree depth: {depth}")
            print(f"  - Short-lived tree depths: alternating {depth} and {depth - 1}")
    finally:
        # Re-enable GC
        gc.enable()


if __name__ == "__main__":
    main()
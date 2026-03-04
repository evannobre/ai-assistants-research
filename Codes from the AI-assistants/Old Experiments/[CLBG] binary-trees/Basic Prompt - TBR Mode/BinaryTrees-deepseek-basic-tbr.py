import sys
import time

class TreeNode:
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"TreeNode(left={self.left is not None}, right={self.right is not None})"

def create_tree(depth):
    """Create a perfect binary tree of given depth"""
    if depth <= 0:
        return TreeNode()
    return TreeNode(create_tree(depth - 1), create_tree(depth - 1))

def walk_tree(node):
    """Walk the tree and count nodes (post-order traversal)"""
    if node is None:
        return 0
    
    left_count = walk_tree(node.left) if node.left else 0
    right_count = walk_tree(node.right) if node.right else 0
    
    return 1 + left_count + right_count

def tree_benchmark(max_depth):
    print(f"Running binary tree benchmark with depth {max_depth}")
    
    # 1. Allocate stretch tree (immediately deallocated by going out of scope)
    print("\n1. Creating stretch tree...")
    stretch_tree = create_tree(max_depth + 1)
    stretch_count = walk_tree(stretch_tree)
    print(f"   Stretch tree depth {max_depth + 1}, node count: {stretch_count}")
    # Stretch tree goes out of scope and becomes eligible for GC
    
    # 2. Create long-lived tree
    print("\n2. Creating long-lived tree...")
    long_lived_tree = create_tree(max_depth)
    long_lived_count = walk_tree(long_lived_tree)
    print(f"   Long-lived tree depth {max_depth}, node count: {long_lived_count}")
    
    # 3. Allocate, walk, and deallocate many trees
    print("\n3. Creating and destroying many trees...")
    min_depth = 4
    
    total_iterations = 0
    start_time = time.time()
    
    for depth in range(min_depth, max_depth + 1, 2):
        iterations = 2 ** (max_depth - depth + min_depth)
        total_iterations += iterations
        
        total_nodes = 0
        for i in range(iterations):
            # Allocate tree
            tree = create_tree(depth)
            
            # Walk tree and count nodes
            node_count = walk_tree(tree)
            total_nodes += node_count
            
            # Tree goes out of scope and becomes eligible for GC
        
        print(f"   Depth {depth}: {iterations} trees, {total_nodes} total nodes")
    
    elapsed_time = time.time() - start_time
    
    # 4. Verify long-lived tree still exists
    print("\n4. Verifying long-lived tree...")
    final_long_lived_count = walk_tree(long_lived_tree)
    if final_long_lived_count == long_lived_count:
        print(f"   ✓ Long-lived tree intact: {final_long_lived_count} nodes")
    else:
        print(f"   ✗ Long-lived tree corrupted!")
        return False
    
    print(f"\nBenchmark completed:")
    print(f"  Total iterations: {total_iterations}")
    print(f"  Total time: {elapsed_time:.3f} seconds")
    
    # Force garbage collection to show everything works
    import gc
    gc.collect()
    print(f"  Garbage collection completed")
    
    return True

if __name__ == "__main__":
    # Use command line argument or default to 21
    try:
        depth = int(sys.argv[1]) if len(sys.argv) > 1 else 21
    except ValueError:
        depth = 21
    
    if depth < 4:
        print("Depth must be at least 4")
        sys.exit(1)
    
    success = tree_benchmark(depth)
    sys.exit(0 if success else 1)
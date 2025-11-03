import sys
import time

# ----------------------------------------------------------------------
# 1. Define a tree node class and methods
# ----------------------------------------------------------------------
class Node:
    """
    A simple node for a binary tree. Leaf nodes and interior nodes 
    are the same memory allocation, as required.
    """
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    @staticmethod
    def item_check(node):
        """Walk the tree, counting nodes. Returns the total node count."""
        if node is None:
            return 0
        return Node.item_check(node.left) + Node.item_check(node.right) + 1

# ----------------------------------------------------------------------
# Helper function to create a perfect binary tree bottom-up
# ----------------------------------------------------------------------
def create_tree(depth):
    """
    Allocates a perfect binary tree of a given depth, bottom-up.
    """
    if depth == 0:
        # Base case: A leaf node
        return Node() 
    else:
        # Recursive step: Interior node
        return Node(create_tree(depth - 1), create_tree(depth - 1))

# ----------------------------------------------------------------------
# Tree creation and performance measurement
# ----------------------------------------------------------------------
def run_tree_work(max_depth):
    """
    Performs the required tree allocation, walk, and deallocation steps.
    """
    min_depth = 4 # Smallest depth for the bottom-up trees

    # Total number of nodes in a perfect binary tree is 2^(depth+1) - 1
    # Checksum is calculated by simply walking and counting the nodes.
    
    print(f"Starting binary tree memory test with max_depth: {max_depth}\n")
    
    
    ## Phase 1: Allocate a binary tree to "stretch" memory (Allocation #1)
    
    # Depth is one higher than the max_depth to ensure it's a 'stretch'
    stretch_depth = max_depth + 1
    print(f"1. Allocating a 'stretch' tree of depth {stretch_depth}...")
    start_time = time.time()
    
    stretch_tree = create_tree(stretch_depth)
    
    # Check it exists and measure memory usage implicitly by traversing
    stretch_count = Node.item_check(stretch_tree)
    end_time = time.time()
    
    print(f"   Stretch tree node count (checksum): {stretch_count}")
    print(f"   Time taken: {end_time - start_time:.4f}s")
    
    # Deallocate it (by letting the variable go out of scope or setting to None, 
    # relying on Python's GC to collect it later).
    del stretch_tree
    # Python's GC is automatic. We don't call gc.collect() to honor the
    # requirement to "use default Garbage Collected techniques."
    print("   'Stretch' tree deallocated (GC expected).\n")


    ## Phase 2: Allocate a long-lived binary tree (Allocation #2)

    long_lived_depth = max_depth
    print(f"2. Allocating a 'long-lived' tree of depth {long_lived_depth}...")
    start_time = time.time()
    
    # This tree will persist until the end of the function
    long_lived_tree = create_tree(long_lived_depth)
    
    long_lived_count_initial = Node.item_check(long_lived_tree)
    end_time = time.time()
    
    print(f"   'Long-lived' tree node count (initial checksum): {long_lived_count_initial}")
    print(f"   Time taken: {end_time - start_time:.4f}s\n")


    ## Phase 3: Allocate, walk, and deallocate many bottom-up binary trees
    # (Allocation #3 and subsequent allocations)

    print("3. Allocating, walking, and deallocating many bottom-up trees:")
    
    total_nodes_allocated = 0
    total_trees_allocated = 0
    start_time = time.time()
    
    # Loop over depths from min_depth up to max_depth
    for depth in range(min_depth, max_depth + 1, 2):
        # We perform the operation twice: once for a smaller number of large trees,
        # and once for a larger number of small trees, as is common in such benchmarks.
        
        # Iteration A: Focus on large trees (fewer allocations)
        iterations_a = 2 
        # Number of nodes needed to reach a comparable total node count
        
        # Iteration B: Focus on small trees (many allocations)
        # The number of iterations to fill the time/memory gap created by the larger tree
        iterations_b = 2 ** (max_depth - depth + min_depth) 
        
        
        # Sub-step 3A: Smaller number of large trees
        for _ in range(iterations_a):
            total_trees_allocated += 1
            # Allocate a tree (Allocation #3, #4, etc.)
            tree = create_tree(depth)
            
            # Walk the tree, counting the nodes
            count = Node.item_check(tree)
            total_nodes_allocated += count

            # Deallocate the tree (relying on GC)
            del tree
            
        # Sub-step 3B: Larger number of small trees
        for _ in range(iterations_b):
            total_trees_allocated += 1
            # Allocate a tree
            tree = create_tree(min_depth)
            
            # Walk the tree, counting the nodes
            count = Node.item_check(tree)
            total_nodes_allocated += count

            # Deallocate the tree (relying on GC)
            del tree

        print(f"   Completed depth {depth}. Total trees: {total_trees_allocated}, Total nodes: {total_nodes_allocated}")

    end_time = time.time()
    print(f"\n   Total time for bottom-up trees: {end_time - start_time:.4f}s")
    print(f"   Total trees allocated: {total_trees_allocated}")
    print(f"   Total nodes allocated/walked: {total_nodes_allocated}\n")


    ## Phase 4: Check that the long-lived binary tree still exists
    
    print("4. Final check of the 'long-lived' tree...")
    start_time = time.time()
    
    # Check the count again to ensure it hasn't been corrupted or prematurely collected
    long_lived_count_final = Node.item_check(long_lived_tree)
    
    # The final checksum *must* match the initial checksum.
    if long_lived_count_final == long_lived_count_initial:
        print(f"   SUCCESS: Final checksum matches initial. Count: {long_lived_count_final}")
    else:
        print(f"   FAILURE: Checksum mismatch! Initial: {long_lived_count_initial}, Final: {long_lived_count_final}")

    end_time = time.time()
    print(f"   Time taken for final check: {end_time - start_time:.4f}s")

# ----------------------------------------------------------------------
# Execution Block
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Get the command line argument for the maximum depth
    # Use 21 as the default if no argument is provided, as requested for performance check.
    try:
        if len(sys.argv) > 1:
            MAX_DEPTH = int(sys.argv[1])
        else:
            MAX_DEPTH = 21 # Default for performance check
    except ValueError:
        print("Error: The argument must be an integer.")
        sys.exit(1)
    
    # A depth of 21 results in a tree with 2^(21+1) - 1 = 4,194,303 nodes. 
    # This stresses memory and GC.
    run_tree_work(MAX_DEPTH)
import sys
import gc
import weakref
import time

class TreeNode:
    """Tree node class with left and right children"""
    __slots__ = ('left', 'right', 'data')
    
    def __init__(self, left=None, right=None, data=None):
        self.left = left
        self.right = right
        self.data = data
    
    def __repr__(self):
        return f"TreeNode(data={self.data})"

class BinaryTreeManager:
    """Manages tree operations following the specified requirements"""
    
    def __init__(self):
        self.long_lived_tree = None
    
    def create_perfect_tree(self, depth, data_fn=None):
        """Create a perfect binary tree of given depth using bottom-up allocation"""
        if depth < 0:
            return None
        
        def build_bottom_up(current_depth):
            if current_depth == 0:
                # Leaf node
                data = data_fn(current_depth) if data_fn else None
                return TreeNode(data=data)
            else:
                # Interior node - build children first (bottom-up)
                left_child = build_bottom_up(current_depth - 1)
                right_child = build_bottom_up(current_depth - 1)
                data = data_fn(current_depth) if data_fn else None
                return TreeNode(left=left_child, right=right, data=data)
        
        return build_bottom_up(depth)
    
    def walk_tree_count_nodes(self, node):
        """Walk the tree and count all nodes"""
        if node is None:
            return 0
        
        count = 1  # Count current node
        count += self.walk_tree_count_nodes(node.left)
        count += self.walk_tree_count_nodes(node.right)
        return count
    
    def allocate_stretch_tree(self, depth):
        """Allocate stretch tree, check it exists, and deallocate it"""
        print(f"  Allocating stretch tree of depth {depth}")
        
        # Create stretch tree
        stretch_tree = self.create_perfect_tree(depth, lambda d: f"stretch_{d}")
        
        # Check it exists by walking and counting
        expected_nodes = 2 ** (depth + 1) - 1
        actual_nodes = self.walk_tree_count_nodes(stretch_tree)
        
        print(f"  Stretch tree has {actual_nodes} nodes (expected: {expected_nodes})")
        
        # Verify it exists
        if actual_nodes != expected_nodes:
            raise RuntimeError(f"Stretch tree verification failed!")
        
        # Explicitly deallocate by breaking references
        stretch_tree = None
        print("  Stretch tree deallocated")
    
    def allocate_long_lived_tree(self, depth):
        """Allocate long-lived tree that persists through other operations"""
        print(f"Allocating long-lived tree of depth {depth}")
        
        self.long_lived_tree = self.create_perfect_tree(
            depth, 
            lambda d: f"long_lived_{d}"
        )
        
        # Verify it was created
        expected_nodes = 2 ** (depth + 1) - 1
        actual_nodes = self.walk_tree_count_nodes(self.long_lived_tree)
        
        print(f"Long-lived tree has {actual_nodes} nodes")
        
        if actual_nodes != expected_nodes:
            raise RuntimeError("Long-lived tree verification failed!")
    
    def allocate_walk_deallocate_trees(self, min_depth, max_depth):
        """Allocate, walk, and deallocate many bottom-up binary trees"""
        print("Allocating, walking, and deallocating many trees...")
        
        for depth in range(min_depth, max_depth + 1):
            iterations = 2 ** (max_depth - depth + min_depth)
            
            print(f"  Depth {depth}: {iterations} iterations")
            
            total_nodes_allocated = 0
            total_nodes_counted = 0
            
            for i in range(iterations):
                # Allocate tree
                tree = self.create_perfect_tree(
                    depth, 
                    lambda d, idx=i: f"temp_{idx}_{d}"
                )
                
                # Walk tree and count nodes
                node_count = self.walk_tree_count_nodes(tree)
                total_nodes_counted += node_count
                
                expected_nodes = 2 ** (depth + 1) - 1
                total_nodes_allocated += expected_nodes
                
                # Deallocate tree by breaking reference
                tree = None
            
            print(f"    Allocated {total_nodes_allocated} nodes, counted {total_nodes_counted} nodes")
            
            if total_nodes_allocated != total_nodes_counted:
                raise RuntimeError(f"Node count mismatch at depth {depth}")
    
    def check_long_lived_tree_exists(self):
        """Verify that the long-lived tree still exists"""
        if self.long_lived_tree is None:
            raise RuntimeError("Long-lived tree is missing!")
        
        # Do a basic walk to verify it's still accessible
        node_count = self.walk_tree_count_nodes(self.long_lived_tree)
        print(f"Long-lived tree verification: {node_count} nodes (still exists)")
        
        return node_count > 0

def main():
    # Use command line argument or default to 21 for performance testing
    if len(sys.argv) > 1:
        try:
            max_depth = int(sys.argv[1])
        except ValueError:
            max_depth = 21
    else:
        max_depth = 21
    
    print(f"Binary Tree Allocator - Max Depth: {max_depth}")
    print("=" * 50)
    
    # Set up GC to be more aggressive for demonstration
    gc.set_threshold(50, 10, 10)
    
    manager = BinaryTreeManager()
    
    # 1. Allocate stretch memory tree
    stretch_depth = max_depth + 1
    print("1. Stretch tree allocation:")
    manager.allocate_stretch_tree(stretch_depth)
    print()
    
    # Force GC to demonstrate deallocation
    gc.collect()
    
    # 2. Allocate long-lived tree
    long_lived_depth = max_depth
    print("2. Long-lived tree allocation:")
    manager.allocate_long_lived_tree(long_lived_depth)
    print()
    
    # 3. Allocate, walk, and deallocate many trees
    min_depth = 4
    print("3. Multiple tree operations:")
    start_time = time.time()
    
    manager.allocate_walk_deallocate_trees(min_depth, max_depth)
    
    end_time = time.time()
    print(f"Multiple tree operations completed in {end_time - start_time:.3f} seconds")
    print()
    
    # Force GC between operations
    gc.collect()
    
    # 4. Verify long-lived tree still exists
    print("4. Long-lived tree verification:")
    manager.check_long_lived_tree_exists()
    
    # Final statistics
    print("\n" + "=" * 50)
    print("Final GC statistics:")
    print(f"GC count: {gc.get_count()}")
    
    # Demonstrate that we're using Python's native GC
    objects = gc.get_objects()
    tree_nodes = [obj for obj in objects if isinstance(obj, TreeNode)]
    print(f"Approximate TreeNode instances in memory: {len(tree_nodes)}")

if __name__ == "__main__":
    main()
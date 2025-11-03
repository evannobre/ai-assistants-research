import sys
from collections import deque
from typing import Optional

class Node:
    """
    Node class that uses memory address as implicit value.
    No traditional data is stored - the existence and address is the value.
    """
    __slots__ = ('left', 'right', '_id')
    
    def __init__(self):
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None
        # Use object id (memory address) as implicit identifier
        self._id = id(self)
    
    @property
    def value(self):
        """Value derived from memory address"""
        return self._id
    
    def __repr__(self):
        return f"Node@{hex(self._id)}"


class BalancedBinaryTree:
    """
    Creates a perfectly balanced binary tree using only memory allocation.
    Uses native Python libraries for queue operations and calculations.
    """
    
    def __init__(self):
        self.root: Optional[Node] = None
        self.size = 0
    
    def build_perfect_tree(self, height: int) -> Node:
        """
        Build a perfect balanced tree of given height using level-order insertion.
        Uses collections.deque for O(1) queue operations.
        
        Args:
            height: Height of the tree (0 = just root)
        
        Returns:
            Root node of the created tree
        """
        if height < 0:
            return None
        
        # Calculate total nodes for perfect tree: 2^(h+1) - 1
        total_nodes = (1 << (height + 1)) - 1  # Bit shift for 2^(h+1)
        
        # Create root
        self.root = Node()
        self.size = 1
        
        if height == 0:
            return self.root
        
        # Use deque for efficient BFS traversal
        queue = deque([self.root])
        current_level = 0
        
        while self.size < total_nodes and queue:
            level_size = len(queue)
            
            for _ in range(level_size):
                node = queue.popleft()
                
                # Add left child
                if self.size < total_nodes:
                    node.left = Node()
                    queue.append(node.left)
                    self.size += 1
                
                # Add right child
                if self.size < total_nodes:
                    node.right = Node()
                    queue.append(node.right)
                    self.size += 1
            
            current_level += 1
        
        return self.root
    
    def get_height(self, node: Optional[Node] = None) -> int:
        """Calculate tree height recursively using native max()"""
        if node is None:
            node = self.root
        
        if node is None:
            return -1
        
        return 1 + max(self.get_height(node.left), self.get_height(node.right))
    
    def is_balanced(self, node: Optional[Node] = None) -> bool:
        """Check if tree is balanced using native abs() and recursion"""
        if node is None:
            node = self.root
        
        if node is None:
            return True
        
        left_height = self.get_height(node.left)
        right_height = self.get_height(node.right)
        
        # Check balance condition and recurse
        return (abs(left_height - right_height) <= 1 and
                self.is_balanced(node.left) and
                self.is_balanced(node.right))
    
    def level_order_traversal(self) -> list:
        """
        BFS traversal using collections.deque.
        Returns list of memory addresses representing nodes.
        """
        if not self.root:
            return []
        
        result = []
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            result.append(node.value)  # Memory address
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        return result
    
    def get_memory_usage(self) -> dict:
        """
        Calculate memory usage using sys.getsizeof().
        Shows actual memory allocation without stored values.
        """
        if not self.root:
            return {'total_bytes': 0, 'node_count': 0}
        
        total_bytes = 0
        queue = deque([self.root])
        node_count = 0
        
        while queue:
            node = queue.popleft()
            total_bytes += sys.getsizeof(node)
            node_count += 1
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        return {
            'total_bytes': total_bytes,
            'node_count': node_count,
            'avg_bytes_per_node': total_bytes / node_count if node_count > 0 else 0
        }
    
    def visualize(self, node: Optional[Node] = None, prefix: str = "", is_left: bool = True) -> str:
        """Generate ASCII visualization of the tree structure"""
        if node is None:
            node = self.root
        
        if node is None:
            return ""
        
        result = []
        
        # Add right subtree
        if node.right:
            result.append(self.visualize(node.right, 
                                        prefix + ("│   " if is_left else "    "), 
                                        False))
        
        # Add current node
        result.append(prefix + ("└── " if is_left else "┌── ") + 
                     f"@{hex(node.value)[-6:]}")
        
        # Add left subtree
        if node.left:
            result.append(self.visualize(node.left, 
                                        prefix + ("    " if is_left else "│   "), 
                                        True))
        
        return "\n".join(result)


# Demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("Memory-Based Balanced Binary Tree Algorithm")
    print("=" * 60)
    
    # Create a perfect balanced tree of height 3
    tree = BalancedBinaryTree()
    tree.build_perfect_tree(height=3)
    
    print(f"\n✓ Created perfect tree with height: {tree.get_height()}")
    print(f"✓ Total nodes allocated: {tree.size}")
    print(f"✓ Is balanced: {tree.is_balanced()}")
    
    # Show memory usage
    mem_info = tree.get_memory_usage()
    print(f"\n📊 Memory Allocation:")
    print(f"   Total bytes: {mem_info['total_bytes']}")
    print(f"   Nodes: {mem_info['node_count']}")
    print(f"   Avg per node: {mem_info['avg_bytes_per_node']:.2f} bytes")
    
    # Show level-order traversal (memory addresses)
    print(f"\n🔍 Level-order traversal (memory addresses):")
    addresses = tree.level_order_traversal()
    for i, addr in enumerate(addresses[:8]):  # Show first 8
        print(f"   Node {i}: {hex(addr)}")
    if len(addresses) > 8:
        print(f"   ... and {len(addresses) - 8} more nodes")
    
    # Visualize tree structure
    print(f"\n🌳 Tree Structure Visualization:")
    print(tree.visualize())
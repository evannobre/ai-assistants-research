import ctypes
import math

class Node(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("left", ctypes.c_void_p),
        ("right", ctypes.c_void_p)
    ]

def build_perfect_binary_tree(depth):
    if depth <= 0:
        return None
    
    total_nodes = 2**depth - 1
    node_size = ctypes.sizeof(Node)
    
    # Allocate contiguous memory
    memory_pool = (Node * total_nodes)()
    
    # Initialize all nodes
    for i in range(total_nodes):
        node = memory_pool[i]
        node.id = i
        
        left_idx = 2 * i + 1
        right_idx = 2 * i + 2
        
        if left_idx < total_nodes:
            node.left = ctypes.addressof(memory_pool[left_idx])
        if right_idx < total_nodes:
            node.right = ctypes.addressof(memory_pool[right_idx])
    
    # Prevent garbage collection by keeping reference
    import gc
    gc.disable()
    
    # Return root and keep reference to memory pool
    return ctypes.addressof(memory_pool[0]), memory_pool
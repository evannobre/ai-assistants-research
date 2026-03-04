# Perfect Binary Tree with Memory Allocation Management

## Overview

This project implements a **perfect binary tree** data structure with explicit memory allocation management, designed for Ubuntu 24.04.4 64-bit systems with 8GB RAM and 256GB SSD.

A perfect binary tree of depth N has these properties:
- Total nodes: `2^(N+1) - 1`
- All internal nodes have exactly 2 children
- All leaf nodes are at the same depth N
- The tree is completely balanced

## Implementations

Two implementations are provided:

### 1. C Implementation (`perfect_binary_tree.c`)
- **Explicit memory management** using `malloc()` and `free()`
- **Memory-efficient** with minimal overhead
- **Fast performance** due to native compilation
- **Direct control** over memory allocation/deallocation
- Suitable for large trees (depth ≤ 30)

### 2. Python Implementation (`perfect_binary_tree.py`)
- **Automatic memory management** with manual GC control
- **Native libraries**: `psutil` for memory monitoring, `collections.deque` for efficient queues
- **Memory-optimized** using `__slots__` in dataclasses
- Better for rapid prototyping and analysis

## System Requirements

| Component | Specification |
|-----------|--------------|
| OS | Ubuntu 24.04.4 64-bit |
| RAM | 8 GB |
| Storage | 256 GB SSD |
| Python | 3.10+ (for Python version) |
| GCC | 11.0+ (for C version) |

## Memory Considerations

### Memory Usage by Depth

| Depth | Total Nodes | C Memory (MB) | Python Memory (MB) |
|-------|-------------|---------------|--------------------|
| 10 | 2,047 | ~0.05 | ~0.2 |
| 15 | 65,535 | ~1.5 | ~6 |
| 20 | 1,048,575 | ~24 | ~100 |
| 25 | 33,554,431 | ~768 | ~3,200 |
| 30 | 1,073,741,823 | ~24,576 | N/A (too large) |

**Note**: Python has higher memory overhead due to object metadata.

### Safety Limits

The implementations include built-in safety checks:
- **C version**: Max depth 30 (configurable)
- **Python version**: Dynamic check based on available memory (uses 80% threshold)

## Installation & Usage

### Quick Start

```bash
# Clone or download the files
cd /path/to/project

# Compile and run C version
make
./perfect_tree 10

# Run Python version (requires psutil)
pip install psutil
python3 perfect_binary_tree.py 10
```

### Python Dependencies

```bash
# Install required Python package
pip install psutil

# Or using apt (Ubuntu)
sudo apt install python3-psutil
```

### Compilation (C)

```bash
# Using Makefile
make

# Manual compilation
gcc -O2 -Wall -o perfect_tree perfect_binary_tree.c -lm
```

### Running Examples

```bash
# C version with depth 10
./perfect_tree 10

# Python version with depth 10
python3 perfect_binary_tree.py 10

# Larger tree (C version)
./perfect_tree 20

# Larger tree (Python version)
python3 perfect_binary_tree.py 15
```

## Algorithm Details

### Memory Allocation Strategy

#### C Implementation
1. **Explicit allocation**: Each node allocated via `malloc(sizeof(TreeNode))`
2. **Error handling**: Checks for allocation failures
3. **Explicit deallocation**: Post-order traversal with `free()`
4. **No garbage collection**: Direct memory control

```c
TreeNode* create_node(int value) {
    TreeNode *node = (TreeNode*)malloc(sizeof(TreeNode));
    if (node == NULL) {
        fprintf(stderr, "Error: malloc failed\n");
        exit(EXIT_FAILURE);
    }
    node->value = value;
    node->left = NULL;
    node->right = NULL;
    return node;
}
```

#### Python Implementation
1. **Automatic allocation**: Python handles memory via reference counting
2. **GC disabled during construction**: Improves performance
3. **`__slots__` optimization**: Reduces per-instance memory overhead
4. **Memory monitoring**: Uses `psutil` to track actual usage

```python
@dataclass
class TreeNode:
    __slots__ = ['value', 'left', 'right']
    value: int
    left: Optional['TreeNode']
    right: Optional['TreeNode']
```

### Build Algorithms

#### Iterative BFS Approach (Recommended)
- **Time Complexity**: O(n) where n = 2^(depth+1) - 1
- **Space Complexity**: O(w) where w is max width = 2^depth
- **Advantages**: 
  - No recursion stack overflow
  - Suitable for deep trees
  - Predictable memory usage

```
Algorithm: Iterative BFS Build
Input: depth N
Output: root of perfect binary tree

1. Create root node with value 0
2. Initialize queue with (root, depth=0)
3. Initialize counter = 1
4. While queue is not empty:
   a. Dequeue (node, current_depth)
   b. If current_depth < N:
      - Create left child with value counter++
      - Enqueue (left_child, current_depth+1)
      - Create right child with value counter++
      - Enqueue (right_child, current_depth+1)
5. Return root
```

#### Recursive Approach (For Shallow Trees)
- **Time Complexity**: O(n)
- **Space Complexity**: O(depth) for recursion stack
- **Advantages**:
  - Elegant and concise
  - Natural tree structure
- **Limitations**:
  - Stack overflow for depth > ~1000 (Python)
  - Limited by system stack size

### Verification Algorithm

The implementation includes a verification function to ensure the tree is perfect:

```
Algorithm: Verify Perfect Tree
Input: root node, expected_depth
Output: boolean (true if perfect)

1. Define helper function get_depth(node):
   a. If node is NULL, return -1
   b. left_depth = get_depth(node.left)
   c. right_depth = get_depth(node.right)
   d. If left_depth ≠ right_depth, return error
   e. If one child NULL but not other, return error
   f. Return left_depth + 1

2. calculated_depth = get_depth(root)
3. Return calculated_depth == expected_depth
```

## Features

### Both Implementations Include:

1. ✓ **Memory requirement calculation** before allocation
2. ✓ **Safety checks** to prevent system crashes
3. ✓ **Build time measurement**
4. ✓ **Memory usage monitoring**
5. ✓ **Tree verification** (ensures perfect structure)
6. ✓ **Node counting**
7. ✓ **In-order traversal** (for small trees)
8. ✓ **Garbage collection testing** (shows memory retention and release)

### C-Specific Features:
- Direct memory allocation with `malloc()`
- Explicit deallocation with `free()`
- Memory usage via `getrusage()`
- Node size: 24 bytes (on 64-bit systems)

### Python-Specific Features:
- GC control with `gc.disable()` / `gc.enable()`
- Memory profiling with `psutil`
- `__slots__` for memory optimization
- Dynamic memory checking

## Performance Analysis

### Build Time Performance

Testing on Intel i7 (example):

| Depth | Nodes | C Time (sec) | Python Time (sec) |
|-------|-------|--------------|-------------------|
| 10 | 2,047 | 0.000050 | 0.001200 |
| 15 | 65,535 | 0.001500 | 0.035000 |
| 20 | 1,048,575 | 0.025000 | 0.580000 |
| 25 | 33,554,431 | 0.850000 | 22.000000 |

**C is typically 20-30x faster** for tree construction.

### Memory Efficiency

- **C**: ~24 bytes per node (struct size)
- **Python**: ~64-72 bytes per node (with object overhead)

**C is approximately 3x more memory efficient**.

## Advanced Usage

### Custom Depth Testing

```bash
# Test with various depths
for depth in 10 15 20; do
    echo "Testing depth: $depth"
    ./perfect_tree $depth
done
```

### Memory Stress Testing

```bash
# C version - large tree
./perfect_tree 25  # ~33 million nodes, ~768 MB

# Python version - moderate tree
python3 perfect_binary_tree.py 20  # ~1 million nodes, ~100 MB
```

### Profiling

```bash
# C version with time and memory profiling
/usr/bin/time -v ./perfect_tree 20

# Python version with memory profiling
python3 -m memory_profiler perfect_binary_tree.py 15
```

## Code Structure

### C Implementation Structure
```
perfect_binary_tree.c
├── TreeNode struct (value, left, right)
├── Queue implementation (for BFS)
├── create_node() - malloc allocation
├── build_tree_iterative() - BFS construction
├── build_tree_recursive() - recursive construction
├── free_tree() - explicit deallocation
├── verify_perfect_tree() - validation
├── count_nodes() - node counting
└── main() - orchestration and monitoring
```

### Python Implementation Structure
```
perfect_binary_tree.py
├── TreeNode dataclass (with __slots__)
├── PerfectBinaryTree class
│   ├── calculate_memory_requirements()
│   ├── build_iterative() - BFS construction
│   ├── build_recursive() - recursive construction
│   ├── verify_perfect_tree() - validation
│   ├── count_nodes() - node counting
│   ├── traverse_inorder() - traversal
│   └── get_memory_usage() - psutil monitoring
└── main() - orchestration and monitoring
```

## Troubleshooting

### Common Issues

**1. Out of Memory Error**
```
Solution: Reduce tree depth
- C: Max safe depth ~30
- Python: Max safe depth ~20
```

**2. Python psutil Not Found**
```bash
pip install psutil
# or
sudo apt install python3-psutil
```

**3. Stack Overflow (Recursive Build)**
```
Solution: Use iterative build or increase stack size
ulimit -s unlimited  # Increase stack size (Linux)
```

**4. Compilation Errors (C)**
```bash
# Ensure GCC is installed
sudo apt install build-essential
```

## Technical Details

### Memory Layout (C)

```
TreeNode structure (64-bit system):
┌─────────────┬──────────────────┐
│   value     │      4 bytes     │
│  (padding)  │      4 bytes     │
│   *left     │      8 bytes     │
│   *right    │      8 bytes     │
└─────────────┴──────────────────┘
Total: 24 bytes per node
```

### GC Behavior (Python)

1. **Construction Phase**: GC disabled for performance
2. **Retention Phase**: Tree kept in memory via references
3. **Cleanup Phase**: References deleted, GC triggered
4. **Memory Release**: Objects collected and freed

## References

### Memory Management
- Linux `malloc()`: glibc documentation
- Python Memory Management: https://docs.python.org/3/c-api/memory.html
- Python GC: https://docs.python.org/3/library/gc.html

### Data Structures
- Binary Trees: *Introduction to Algorithms* (CLRS)
- Perfect Binary Trees: https://en.wikipedia.org/wiki/Binary_tree#Types_of_binary_trees

### System Programming
- `getrusage()`: `man 2 getrusage`
- psutil: https://psutil.readthedocs.io/

## License

This implementation is provided for educational purposes.

## Author

Computer Scientist specializing in back-end development with expertise in:
- Memory allocation and management
- Data structures and algorithms
- System-level programming (C)
- High-level scripting (Python)
- Performance optimization

---

**Last Updated**: January 2026
**Target Platform**: Ubuntu 24.04.4 64-bit, 8GB RAM, 256GB SSD

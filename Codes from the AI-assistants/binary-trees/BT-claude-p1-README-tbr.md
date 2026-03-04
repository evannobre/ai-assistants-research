# Perfect Binary Tree Memory Allocation Algorithm

## Overview

This repository contains implementations of a memory allocation algorithm that creates a perfect binary tree of depth N using native libraries from different programming languages. The algorithm focuses on memory management and allocation tracking **before** any garbage collection occurs.

## Algorithm Description

### What is a Perfect Binary Tree?

A perfect binary tree is a binary tree in which:
- All interior nodes have exactly two children
- All leaf nodes are at the same depth/level
- The tree is completely filled at every level

For a perfect binary tree of depth N:
- **Total nodes** = 2^(N+1) - 1
- **Leaf nodes** = 2^N
- **Internal nodes** = 2^N - 1

### Core Algorithm

```
ALGORITHM: AllocatePerfectBinaryTree(currentDepth, targetDepth, nodeValue)

INPUT: 
  - currentDepth: Current level in the tree (0-indexed)
  - targetDepth: Maximum depth of the tree
  - nodeValue: Value to assign to the current node

OUTPUT:
  - Pointer/reference to the allocated TreeNode or NULL/null

STEPS:
  1. BASE CASE: If currentDepth > targetDepth
     - Return NULL/null (no more nodes to allocate)
  
  2. ALLOCATE NODE:
     - Allocate memory for new TreeNode
     - Assign nodeValue to node
     - Initialize left and right pointers to NULL/null
     - Increment node counter
  
  3. CALCULATE CHILD VALUES (Binary Heap Indexing):
     - leftValue = 2 * nodeValue + 1
     - rightValue = 2 * nodeValue + 2
  
  4. RECURSIVE ALLOCATION:
     - node.left = AllocatePerfectBinaryTree(currentDepth + 1, targetDepth, leftValue)
     - node.right = AllocatePerfectBinaryTree(currentDepth + 1, targetDepth, rightValue)
  
  5. RETURN:
     - Return allocated node

INITIAL CALL: root = AllocatePerfectBinaryTree(0, N, 0)
```

### Complexity Analysis

- **Time Complexity**: O(2^N) 
  - Must allocate 2^(N+1) - 1 nodes
  - Each node allocated in constant time
  
- **Space Complexity**: O(2^N) + O(N)
  - O(2^N) for storing all nodes
  - O(N) for recursion call stack (maximum depth)

### Memory Management Strategy

The implementations demonstrate different memory management approaches:

1. **C Implementation**: 
   - Manual memory management using `malloc()` and `free()`
   - Explicit control over allocation and deallocation
   - No automatic garbage collection

2. **Python Implementation**:
   - Automatic memory management with GC
   - Uses `gc.disable()` to prevent premature collection
   - Uses `tracemalloc` module for memory tracking

3. **Java Implementation**:
   - Heap-based allocation with automatic GC
   - Uses `MemoryMXBean` for memory monitoring
   - Uses `System.gc()` to suggest collection after testing

## File Structure

```
.
├── binary_tree_memory.c      # C implementation (manual memory management)
├── binary_tree_memory.py     # Python implementation (GC control)
├── BinaryTreeMemory.java     # Java implementation (heap management)
└── README.md                 # This file
```

## Implementation Details

### C Implementation

**Key Features:**
- Uses native C `stdlib.h` for `malloc()` and `free()`
- Custom memory tracking wrapper around `malloc()`
- Post-order traversal for safe memory deallocation
- Uses `time.h` for performance measurement

**Compilation and Execution:**
```bash
gcc -o binary_tree_memory binary_tree_memory.c -std=c99
./binary_tree_memory
```

### Python Implementation

**Key Features:**
- Uses native `gc` module for garbage collection control
- Uses `tracemalloc` module for detailed memory tracking
- Uses `dataclasses` for clean node structure
- Uses `sys` module for size calculations

**Execution:**
```bash
python3 binary_tree_memory.py
```

### Java Implementation

**Key Features:**
- Uses `java.lang.management` for memory monitoring
- Uses `MemoryMXBean` for heap usage tracking
- Uses `Runtime` API for runtime information
- Automatic heap management with GC suggestions

**Compilation and Execution:**
```bash
javac BinaryTreeMemory.java
java BinaryTreeMemory
```

## Example Output

For a depth of 5 (63 nodes):

```
============================================================
Allocating Perfect Binary Tree - Depth: 5
Expected nodes: 63
============================================================

Memory Allocation Statistics:
============================================================
  Target depth:           5
  Expected nodes:         63
  Actual nodes allocated: 63
  Status:                 ✓ PASS

  Total memory allocated: 5,040 bytes
  Memory per node (avg):  80.00 bytes
  Allocation calls:       63
  Time taken:             0.000152 seconds
============================================================

⚠️  ALL 63 NODES ARE CURRENTLY IN MEMORY
   No garbage collection - tree is fully allocated
```

## Memory Tracking Features

Each implementation tracks:

1. **Node Count**: Total number of nodes allocated
2. **Memory Usage**: Total bytes allocated for the tree
3. **Memory per Node**: Average memory consumption per node
4. **Allocation Time**: Time taken to allocate entire tree
5. **Verification**: Confirms tree structure is correct

## Testing Strategy

The implementations test with multiple depths:
- Small depths (3-5): Display full tree structure
- Medium depths (8-10): Statistical analysis only
- Large depths (12+): Stress testing (Java only)

Each test:
1. Allocates the complete tree
2. Verifies node count and depth
3. Reports memory statistics
4. **Keeps tree in memory** (pre-GC state)
5. Manually triggers cleanup/GC

## Key Insights

### Memory Patterns

- **C**: Predictable allocation (~24-32 bytes per node on 64-bit systems)
- **Python**: Higher overhead (~80-120 bytes per node due to object metadata)
- **Java**: Medium overhead (~40-80 bytes per node with JVM overhead)

### GC Behavior

- **Before GC**: All nodes remain in memory, fully accessible
- **After cleanup**: 
  - C: Memory immediately freed to OS
  - Python: Eligible for GC, collected in next cycle
  - Java: Eligible for GC, collected when heap pressure increases

## Use Cases

This algorithm and implementation pattern is useful for:

1. **Memory profiling**: Understanding allocation patterns
2. **GC analysis**: Studying garbage collection behavior
3. **Performance testing**: Benchmarking allocation speed
4. **Data structure education**: Learning tree allocation
5. **Memory management**: Comparing manual vs automatic approaches

## Limitations

- **Maximum depth** limited by:
  - Available memory (2^N nodes can consume significant RAM)
  - Stack depth for recursion (typically safe up to depth 20-30)
  
- **For depth 20**: ~2 million nodes, ~160+ MB memory
- **For depth 25**: ~67 million nodes, ~5+ GB memory

## Extensions

Possible enhancements:

1. **Iterative allocation**: Use queue/stack instead of recursion
2. **Memory pooling**: Pre-allocate node blocks
3. **Parallel allocation**: Multi-threaded tree construction
4. **Serialization**: Save/load tree from disk
5. **Compression**: Store tree in compact format

## References

- Perfect Binary Trees: https://en.wikipedia.org/wiki/Binary_tree#Types_of_binary_trees
- Memory Management: Language-specific documentation
- Big-O Complexity: https://en.wikipedia.org/wiki/Time_complexity

## License

This code is provided for educational purposes.

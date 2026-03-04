# Binary Trees Benchmark

This benchmark measures memory allocation and garbage collection performance by creating and destroying many binary trees. It's designed to stress test GC implementations and memory allocators.

## Overview

The benchmark performs the following operations:
1. **Stretch memory** - Allocates a large binary tree, verifies it, then lets it be garbage collected
2. **Create long-lived tree** - Allocates a tree that persists throughout the benchmark
3. **Allocate/deallocate many trees** - Creates, walks, and destroys many trees of varying depths
4. **Verify long-lived tree** - Confirms the long-lived tree still exists after all the churn

## Key Requirements

### Tree Structure
- All nodes (interior and leaf) use the same memory allocation
- Each node has left and right child pointers
- Leaf nodes have null/nil children

### Algorithm
- Trees are perfect binary trees (all interior nodes have 2 children)
- Tree depth determines size: depth N has 2^(N+1) - 1 nodes
- Bottom-up allocation: create children before parents
- The work must not be optimized away

### Memory Management
- **Garbage Collected Languages** (Python, Java, JavaScript, Go): Use native GC
- **Manual Memory Languages** (C++): Use per-node allocation with new/delete
- **No custom allocators**: Don't implement arenas, memory pools, or free lists

## Implementations

### Python (binarytrees.py)

**Compile/Run:**
```bash
python3 binarytrees.py 21
```

**Features:**
- Uses native Python garbage collection
- `__slots__` for memory efficiency
- Trees automatically collected when out of scope

### Java (BinaryTrees.java)

**Compile/Run:**
```bash
javac BinaryTrees.java
java BinaryTrees 21
```

**Features:**
- Uses Java's generational garbage collector
- Private inner TreeNode class
- Automatic memory management

### C++ (binarytrees.cpp)

**Compile/Run:**
```bash
g++ -O3 -o binarytrees binarytrees.cpp
./binarytrees 21
```

**Features:**
- Per-node allocation using standard new/delete
- Explicit deleteTree() for deallocation
- Post-order traversal for proper cleanup
- No custom allocators

### Go (binarytrees.go)

**Compile/Run:**
```bash
go build -o binarytrees binarytrees.go
./binarytrees 21
```

**Features:**
- Uses Go's concurrent garbage collector
- Pointer-based tree nodes
- Automatic memory management

### JavaScript/Node.js (binarytrees.js)

**Run:**
```bash
node binarytrees.js 21
```

**Features:**
- Uses V8's garbage collector
- ES6 class-based implementation
- Automatic memory management

## Usage

All implementations take a single command-line argument: the maximum tree depth.

```bash
<program> <max_depth>
```

**Recommended test depth:** 21

**Example output for depth 21:**
```
stretch tree of depth 22	 check: 8388607
2097152	 trees of depth 4	 check: 65011712
524288	 trees of depth 6	 check: 66584576
131072	 trees of depth 8	 check: 66977792
32768	 trees of depth 10	 check: 67076096
8192	 trees of depth 12	 check: 67100672
2048	 trees of depth 14	 check: 67106816
512	 trees of depth 16	 check: 67108352
128	 trees of depth 18	 check: 67108736
32	 trees of depth 20	 check: 67108832
long lived tree of depth 21	 check: 4194303
```

## Performance Considerations

### Depth Guidelines
- **Small test:** depth 10-14 (runs in seconds)
- **Medium test:** depth 16-18 (runs in tens of seconds)
- **Large test:** depth 20-21 (runs in minutes, stresses GC)
- **Extreme test:** depth 22+ (may run for 10+ minutes or exhaust memory)

### Memory Usage
Each tree of depth N requires approximately:
- Nodes: 2^(N+1) - 1
- Memory: ~16-32 bytes per node (language dependent)
- Depth 21: ~4 million nodes, ~128+ MB per tree

### What the Benchmark Tests
1. **Allocation speed** - Creating millions of small objects
2. **GC efficiency** - Collecting short-lived objects while preserving long-lived ones
3. **Memory pressure** - Exercising different GC generations/regions
4. **Tree traversal** - Cache performance and pointer chasing

## Implementation Notes

### Why These Choices?

**Python:**
- `__slots__` reduces memory overhead per instance
- No manual memory management needed
- GC handles all cleanup automatically

**Java:**
- Modern JVMs have sophisticated generational GC
- Young generation handles short-lived trees efficiently
- Long-lived tree naturally promotes to old generation

**C++:**
- No GC, so explicit new/delete required
- Post-order deletion ensures children freed before parents
- Standard allocator (not custom pool) as required

**Go:**
- Concurrent GC designed for low latency
- Pointers allow GC to track object graphs
- Automatic cleanup like other GC languages

**JavaScript:**
- V8's sophisticated GC with generational collection
- Class syntax for clean, modern code
- Node.js provides stable runtime

### Compliance with Requirements

✅ Perfect binary trees created
✅ At least 4 allocations (millions in practice)
✅ Native libraries/allocators used
✅ Work not optimized away (checkTree counts nodes)
✅ Leaf nodes same as interior nodes
✅ Default GC techniques (no custom tuning)
✅ No custom arenas/pools/freelists
✅ All required steps implemented:
  - Stretch tree allocated and deallocated
  - Long-lived tree created
  - Many bottom-up trees created, walked, deallocated
  - Long-lived tree verified at end

## Verification

To verify correctness, the check sums should match across all implementations for the same depth. The formulas are:

- Tree of depth N has 2^(N+1) - 1 nodes
- For the iteration loop at depth D: iterations × (2^(D+1) - 1) = check sum

Example for depth 21, trees of depth 4:
- Iterations: 2^(21-4+4) = 2^21 = 2,097,152
- Nodes per tree: 2^5 - 1 = 31
- Check sum: 2,097,152 × 31 = 65,011,712 ✓

## License

This is a benchmark implementation following the Computer Language Benchmarks Game specification.

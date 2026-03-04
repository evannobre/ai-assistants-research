# Binary Trees Benchmark - Implementation Guide

## Overview

This benchmark tests memory allocation and garbage collection performance by creating and destroying binary trees of various depths. The implementations follow strict requirements to ensure fair comparison across languages.

## Requirements Met

### Core Algorithm Requirements
1. ✅ **Tree Node Definition**: Each implementation defines a tree node class/struct with left and right children
2. ✅ **Stretch Memory**: Allocates a binary tree to stretch memory, checks it exists, then deallocates it
3. ✅ **Long-lived Tree**: Allocates a tree that persists throughout the benchmark
4. ✅ **Bottom-up Trees**: Allocates, walks, and deallocates many trees in a loop
5. ✅ **Final Verification**: Checks that the long-lived tree still exists at the end

### Technical Requirements
- ✅ **Minimum 4 Allocations**: Each tree node requires its own allocation
- ✅ **Native Libraries**: Uses standard library memory management (GC or manual)
- ✅ **Leaf = Interior Nodes**: Same memory allocation strategy for all nodes
- ✅ **No Custom Memory Management**: No arenas, pools, or free lists
- ✅ **No Optimization Away**: Work is performed and verified

## Implementations

### 1. C++ (binarytrees.cpp)
**Memory Management**: Manual allocation with `new`/`delete`
- Uses pointer-based tree structure
- Recursive destructor ensures proper cleanup
- Compiler: g++ with -O3 optimization
- Best for: Maximum performance with manual control

```bash
g++ -O3 -std=c++17 -o binarytrees_cpp binarytrees.cpp
./binarytrees_cpp 21
```

### 2. Java (BinaryTrees.java)
**Memory Management**: Generational garbage collection
- Uses Java's default GC (G1GC on modern JVMs)
- Constructor-based tree building
- Best for: Predictable GC behavior with good throughput

```bash
javac BinaryTrees.java
java BinaryTrees 21
```

**Optional GC tuning** (not required but available):
```bash
# For better performance on large trees
java -XX:+UseG1GC -Xmx4g BinaryTrees 21
```

### 3. Python (binarytrees.py)
**Memory Management**: Reference counting + cyclic GC
- Uses `__slots__` for memory efficiency
- Python's automatic memory management
- Best for: Simplicity and readability

```bash
python3 binarytrees.py 21
```

### 4. Go (binarytrees.go)
**Memory Management**: Concurrent mark-sweep GC
- Pointer-based structures for efficient allocation
- Go's low-latency GC
- Best for: Concurrent performance

```bash
go build -o binarytrees_go binarytrees.go
./binarytrees_go 21
```

### 5. Rust (binarytrees.rs)
**Memory Management**: Ownership-based (RAII with Box)
- `Box<T>` for heap allocation
- Automatic cleanup via Drop trait
- Best for: Memory safety without GC overhead

```bash
rustc -O -o binarytrees_rust binarytrees.rs
./binarytrees_rust 21
```

### 6. C# (BinaryTrees.cs)
**Memory Management**: Generational garbage collection
- Similar to Java's GC approach
- .NET runtime manages memory
- Best for: .NET ecosystem integration

```bash
# With Mono
csc -optimize+ BinaryTrees.cs
mono BinaryTrees.exe 21

# Or with .NET Core/8+
dotnet run -c Release 21
```

## Performance Testing

### Recommended Test Depth: 21
At depth 21, the benchmark creates:
- Stretch tree: 2^22 - 1 = 4,194,303 nodes
- Long-lived tree: 2^21 - 1 = 2,097,151 nodes
- Multiple iterations of trees at various depths

### Memory Requirements
For depth 21:
- Each node typically requires 16-24 bytes (2 pointers)
- Peak memory: ~200-400 MB depending on GC behavior
- Well within 8GB RAM specification

### Running All Benchmarks
```bash
./run_benchmarks.sh 21
```

### Running Individual Tests
```bash
# Quick test (depth 10)
./binarytrees_cpp 10

# Standard test (depth 15)
./binarytrees_go 15

# Performance test (depth 21)
./binarytrees_rust 21
```

## Algorithm Details

### Tree Construction
Trees are built **bottom-up** recursively:
```
makeTree(depth):
    if depth > 0:
        return Node(makeTree(depth-1), makeTree(depth-1))
    else:
        return Node(null, null)
```

### Tree Checking
The check operation counts all nodes:
```
check(node):
    if node.left == null:
        return 1
    return 1 + check(node.left) + check(node.right)
```

### Iteration Counts
For each depth from minDepth to maxDepth (step 2):
- iterations = 2^(maxDepth - depth + minDepth)
- This ensures roughly constant work per depth level

## Best Practices Followed

### 1. Memory Allocation
- ✅ Each node allocated separately (no batching)
- ✅ No custom allocators or memory pools
- ✅ Uses language's native allocation mechanisms

### 2. Garbage Collection
- ✅ Relies on language defaults (no tuning flags required)
- ✅ Trees deallocated naturally (scope exit, GC, or delete)
- ✅ No manual GC hints or forced collections

### 3. Performance
- ✅ No work optimized away (check results are computed and printed)
- ✅ Recursive operations prevent inlining/optimization
- ✅ Leaf nodes same as interior nodes (no special cases)

### 4. Code Quality
- ✅ Clear, readable implementations
- ✅ Idiomatic code for each language
- ✅ Proper error handling (where applicable)
- ✅ Standard library usage

## System Requirements

**Target System**: Ubuntu 24.04.4 64-bit
- **RAM**: 8 GB
- **Storage**: 256 GB SSD
- **Compilers**: g++ 13.x, OpenJDK 21, Python 3.12, Go 1.22, Rust 1.75, .NET 8

All implementations are designed to run efficiently within these constraints.

## Expected Output Format

```
stretch tree of depth 22	 check: 4194303
2097152	 trees of depth 4	 check: 65011712
524288	 trees of depth 6	 check: 66584576
131072	 trees of depth 8	 check: 66977792
32768	 trees of depth 10	 check: 67076096
8192	 trees of depth 12	 check: 67100672
2048	 trees of depth 14	 check: 67106816
512	 trees of depth 16	 check: 67108352
128	 trees of depth 18	 check: 67108736
32	 trees of depth 20	 check: 67108832
long lived tree of depth 21	 check: 2097151
```

## Key Design Decisions

### Why No Custom Memory Management?
To ensure fair comparison across languages using their native memory management systems. Custom allocators would obscure the true performance characteristics of each language's runtime.

### Why Same Allocation for Leaf and Interior Nodes?
This ensures the benchmark measures real-world scenarios where node types aren't known at allocation time. It prevents optimization tricks that wouldn't apply to general-purpose code.

### Why Depth 21?
- Large enough to stress memory systems
- Small enough to complete in reasonable time
- Fits comfortably in 8GB RAM
- Standard benchmark depth for comparison

## Troubleshooting

### Out of Memory
If you encounter OOM errors:
1. Reduce depth: try 19 or 20 instead of 21
2. Check available RAM: `free -h`
3. Close other applications

### Compilation Errors
Ensure you have the required compilers:
```bash
g++ --version    # Should be 11+
java --version   # Should be 17+
python3 --version # Should be 3.10+
go version       # Should be 1.18+
rustc --version  # Should be 1.70+
```

### Slow Performance
Expected runtimes for depth 21:
- C++: 1-3 seconds
- Rust: 1-3 seconds
- Go: 2-5 seconds
- Java: 2-6 seconds (after warmup)
- C#: 2-6 seconds
- Python: 30-60 seconds

## License

These implementations follow the Computer Language Benchmarks Game methodology and are provided as educational examples of proper binary tree allocation benchmarks.

# Binary Trees Benchmark Implementation

## Overview

This repository contains implementations of the binary trees benchmark in multiple languages. The benchmark tests garbage collection and memory allocation performance by creating, traversing, and deallocating binary trees.

## Algorithm Description

Each implementation follows the exact same algorithm:

1. **Stretch Memory**: Allocate a binary tree one level deeper than the maximum depth, verify it exists by counting nodes, then deallocate it
2. **Long-lived Tree**: Allocate a binary tree at maximum depth that persists throughout the benchmark
3. **Bottom-up Trees**: For each depth from min to max (stepping by 2):
   - Calculate number of iterations: `2^(maxDepth - depth + minDepth)`
   - Allocate trees of that depth
   - Walk each tree to count nodes
   - Deallocate the tree
4. **Verify**: Check that the long-lived tree still exists and report its node count

## Key Requirements Met

- **Same Node Type**: Leaf nodes and interior nodes use identical memory allocation (no optimization)
- **At Minimum 4 Allocations**: Each tree requires multiple node allocations based on depth
- **Native Libraries**: All implementations use standard library memory management
- **No Custom Arenas**: Uses language-default GC or per-node allocation (Rust, C++)
- **Work Not Optimized Away**: Trees are walked to count nodes, preventing dead code elimination

## Implementations

### 1. C++ (`binarytrees.cpp`)
- **Memory Management**: Manual per-node allocation with `new`/`delete`
- **Deallocation**: Recursive destructor ensures all nodes are freed
- **Build**: `g++ -O3 -o binarytrees binarytrees.cpp`
- **Run**: `./binarytrees 21`

### 2. Java (`BinaryTrees.java`)
- **Memory Management**: Automatic garbage collection (JVM default)
- **Deallocation**: Nodes become eligible for GC when unreachable
- **Build**: `javac BinaryTrees.java`
- **Run**: `java BinaryTrees 21`

### 3. Python (`binarytrees.py`)
- **Memory Management**: Reference counting + generational GC
- **Deallocation**: `del` statement removes references for faster collection
- **Optimization**: `__slots__` reduces per-instance memory overhead
- **Run**: `python3 binarytrees.py 21`

### 4. Go (`binarytrees.go`)
- **Memory Management**: Concurrent mark-and-sweep garbage collector
- **Deallocation**: Automatic when references go out of scope
- **Build**: `go build -o binarytrees binarytrees.go`
- **Run**: `./binarytrees 21`

### 5. C# (`BinaryTrees.cs`)
- **Memory Management**: Generational garbage collection (.NET runtime)
- **Deallocation**: Automatic GC with multiple generations
- **Build**: `csc BinaryTrees.cs` or `dotnet build`
- **Run**: `mono BinaryTrees.exe 21` or `./BinaryTrees 21`

### 6. Rust (`binarytrees.rs`)
- **Memory Management**: Ownership-based with `Box<T>` heap allocation
- **Deallocation**: Deterministic drop when Box goes out of scope
- **No Runtime GC**: Memory freed immediately when ownership ends
- **Build**: `rustc -O binarytrees.rs`
- **Run**: `./binarytrees 21`

### 7. JavaScript/Node.js (`binarytrees.js`)
- **Memory Management**: V8 generational garbage collector
- **Deallocation**: Automatic when objects become unreachable
- **Run**: `node binarytrees.js 21`

## Performance Characteristics

### Memory Allocation Patterns

For depth N, the number of nodes allocated is: `2^(N+1) - 1`

Examples:
- Depth 4: 31 nodes (4 allocations minimum met)
- Depth 10: 2,047 nodes
- Depth 21: 4,194,303 nodes (~4.2 million)

### GC Pressure

The benchmark creates significant GC pressure by:
- Allocating millions of short-lived objects
- Maintaining one long-lived tree while allocating/deallocating others
- Testing GC's ability to handle multiple generations of objects

## System Requirements

- **OS**: Ubuntu 24.04.4 LTS 64-bit
- **RAM**: 8 GB (sufficient for depth 21)
- **Storage**: SSD 256 GB
- **CPU**: Multi-core recommended for concurrent GC (Go, Java, C#)

## Expected Output (Depth 21)

```
stretch tree of depth 22	 check: 8388607
2097152	 trees of depth 4	 check: 65011712
524288	 trees of depth 6	 check: 66060288
131072	 trees of depth 8	 check: 66584576
32768	 trees of depth 10	 check: 66846720
8192	 trees of depth 12	 check: 66977792
2048	 trees of depth 14	 check: 67043328
512	 trees of depth 16	 check: 67076096
128	 trees of depth 18	 check: 67092480
32	 trees of depth 20	 check: 67100672
long lived tree of depth 21	 check: 4194303
```

## Node Count Verification

The check sum for each iteration verifies correct tree construction:
- Each tree of depth D has `2^(D+1) - 1` nodes
- Iterations × nodes per tree = check sum

## Building and Running All

### Quick Test (Depth 10)
```bash
# C++
g++ -O3 -o binarytrees_cpp binarytrees.cpp && ./binarytrees_cpp 10

# Java
javac BinaryTrees.java && java BinaryTrees 10

# Python
python3 binarytrees.py 10

# Go
go build -o binarytrees_go binarytrees.go && ./binarytrees_go 10

# Rust
rustc -O -o binarytrees_rust binarytrees.rs && ./binarytrees_rust 10

# JavaScript
node binarytrees.js 10
```

### Full Benchmark (Depth 21)
Replace `10` with `21` in the commands above.

**Warning**: Depth 21 may take several minutes and use significant memory (1-4 GB depending on language).

## Implementation Notes

### Why These Approaches?

1. **C++**: Manual memory management represents explicit control baseline
2. **Java/C#**: Enterprise GC implementations with tuning options
3. **Python**: High-level scripting with GC, showcasing interpreter overhead
4. **Go**: Modern concurrent GC designed for low-latency
5. **Rust**: Zero-cost abstractions with no runtime GC overhead
6. **JavaScript**: V8 engine optimization and hidden class optimizations

### Memory Efficiency

Languages ranked by approximate memory usage (depth 21):
1. Rust (most efficient - no GC overhead)
2. C++ (manual management)
3. Go (efficient concurrent GC)
4. Java (tuned GC, object overhead)
5. C# (similar to Java)
6. JavaScript (V8 overhead)
7. Python (highest overhead - dynamic typing)

### Speed Rankings (Typical)

1. C++ / Rust (compiled, optimized)
2. Go (compiled, efficient GC)
3. Java (JIT compilation after warmup)
4. C# (JIT compilation)
5. JavaScript (V8 JIT)
6. Python (interpreted, slower)

## License

Public domain / MIT - These are standard benchmark implementations.

## References

- Based on "The Computer Language Benchmarks Game" binary-trees specification
- Tests GC efficiency and allocation performance
- Demonstrates memory management patterns across language paradigms

package main

import (
	"errors"
	"fmt"
	"math"
	"math/bits"
	"os"
	"strconv"
)

type Node struct {
	// Store child links as indices to avoid pointers (reduces GC work).
	Left  int32
	Right int32

	// Optional payload (keep it small if you want max depth).
	Value uint32
}

// BuildPerfectTree builds a perfect binary tree of depth N (root depth = 0)
// using a single contiguous allocation.
//
// It returns the node array (arena), and the root index (always 0 when non-empty).
func BuildPerfectTree(N uint) ([]Node, int32, error) {
	// nodes = 2^(N+1) - 1
	if N >= uint(bits.UintSize-1) {
		return nil, -1, errors.New("N too large for this architecture (overflow risk)")
	}
	pow := uint64(1) << (N + 1)
	nodesCount64 := pow - 1

	// Rough memory guard for an 8 GB machine.
	// Node is small: Left(4) + Right(4) + Value(4) => typically 12 bytes, often padded to 16.
	// We assume 16 bytes/node for safety. Keep headroom for OS + runtime.
	const safetyNodeBytes = 16
	const maxBytes = uint64(6) * 1024 * 1024 * 1024 // ~6 GiB budget
	estBytes := nodesCount64 * safetyNodeBytes
	if estBytes > maxBytes {
		return nil, -1, fmt.Errorf("tree too large: depth=%d => %d nodes, ~%.2f GiB estimated > %.2f GiB budget",
			N, nodesCount64, float64(estBytes)/math.Pow(1024, 3), float64(maxBytes)/math.Pow(1024, 3))
	}

	// Go slice length is int, so check conversion.
	if nodesCount64 > uint64(^uint(0)>>1) {
		return nil, -1, errors.New("node count exceeds max slice length")
	}
	nodesCount := int(nodesCount64)

	// Single allocation for all nodes.
	nodes := make([]Node, nodesCount)

	// Fill links.
	// For a perfect binary tree in array form:
	// left(i) = 2i+1, right(i) = 2i+2
	for i := 0; i < nodesCount; i++ {
		l := 2*i + 1
		r := 2*i + 2

		if l < nodesCount {
			nodes[i].Left = int32(l)
		} else {
			nodes[i].Left = -1
		}
		if r < nodesCount {
			nodes[i].Right = int32(r)
		} else {
			nodes[i].Right = -1
		}

		// Example payload (optional)
		nodes[i].Value = uint32(i)
	}

	if nodesCount == 0 {
		return nodes, -1, nil
	}
	return nodes, 0, nil
}

// Example: compute sum of values (iterative stack, no recursion).
func SumValues(nodes []Node, root int32) uint64 {
	if root < 0 {
		return 0
	}
	var sum uint64
	stack := make([]int32, 0, 64)
	stack = append(stack, root)

	for len(stack) > 0 {
		n := stack[len(stack)-1]
		stack = stack[:len(stack)-1]

		sum += uint64(nodes[n].Value)

		if nodes[n].Left >= 0 {
			stack = append(stack, nodes[n].Left)
		}
		if nodes[n].Right >= 0 {
			stack = append(stack, nodes[n].Right)
		}
	}
	return sum
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <depth N>\nExample: %s 24\n", os.Args[0], os.Args[0])
		os.Exit(2)
	}
	n64, err := strconv.ParseUint(os.Args[1], 10, 32)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Invalid N:", err)
		os.Exit(2)
	}

	nodes, root, err := BuildPerfectTree(uint(n64))
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}

	fmt.Printf("Built perfect binary tree: depth=%d, nodes=%d, root=%d\n", n64, len(nodes), root)
	fmt.Printf("Sum(values)=%d\n", SumValues(nodes, root))
}


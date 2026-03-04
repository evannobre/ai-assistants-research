/*
 * The Computer Language Benchmarks Game
 * Binary Trees Implementation
 *
 * Specialized for: Back-end Best Practices (RAII, Native Concurrency)
 * Constraints: Per-node allocation, No custom arenas, Std Lib only.
 */

#include <iostream>
#include <cstdlib>
#include <algorithm>
#include <vector>
#include <future>   // Native library for concurrency
#include <iomanip>  // For output formatting

// ---------------------------------------------------------------------
// 1. Define a tree node class
// ---------------------------------------------------------------------
// Requirement: "Leaf nodes must be the same as interior nodes"
struct Node {
    Node *left;
    Node *right;

    // Requirement: "Allocate a binary tree" (Per node allocation via 'new')
    Node(int depth) {
        if (depth > 0) {
            left = new Node(depth - 1);
            right = new Node(depth - 1);
        } else {
            left = nullptr;
            right = nullptr;
        }
    }

    // Requirement: "Deallocate it" (Recursive destruction)
    ~Node() {
        if (left) {
            delete left;
            delete right;
        }
    }

    // Requirement: "Walk the tree, counting the nodes"
    // Using a checksum logic common to this benchmark
    int check() const {
        if (left)
            return left->check() + right->check() + 1;
        else
            return 1;
    }
};

// Helper to encapsulate the "Allocate, Walk, Deallocate" lifecycle
int make_check_deallocate(int depth) {
    Node* t = new Node(depth);
    int c = t->check();
    delete t;
    return c;
}

int main(int argc, char* argv[]) {
    // -----------------------------------------------------------------
    // Configuration & Input
    // -----------------------------------------------------------------
    // Requirement: "Use a larger command line argument (21)"
    // Minimum depth is set to 4 as per standard benchmark spec.
    const int min_depth = 4;
    int max_depth = (argc >= 2) ? std::stoi(argv[1]) : 10;
    
    // Ensure max_depth is at least min_depth + 2 for the logic to hold
    if (max_depth < min_depth + 2) {
        max_depth = min_depth + 2;
    }

    // -----------------------------------------------------------------
    // 2. Allocate a binary tree to "stretch" memory
    // -----------------------------------------------------------------
    {
        int stretch_depth = max_depth + 1;
        int check = make_check_deallocate(stretch_depth);
        
        std::cout << "stretch tree of depth " << stretch_depth 
                  << "\t check: " << check << std::endl;
    }

    // -----------------------------------------------------------------
    // 3. Allocate a long-lived binary tree
    // -----------------------------------------------------------------
    // This tree lives on while others are allocated/deallocated
    Node* long_lived_tree = new Node(max_depth);

    // -----------------------------------------------------------------
    // 4. Allocate, walk, and deallocate many bottom-up binary trees
    // -----------------------------------------------------------------
    // We use std::vector to store results to preserve output order
    // while processing in parallel (Back-end best practice).
    
    struct Result {
        int depth;
        int iterations;
        int check;
    };
    
    std::vector<std::future<Result>> tasks;

    for (int d = min_depth; d <= max_depth; d += 2) {
        // Calculate iterations: 1 << (max_depth - d + min_depth)
        int iterations = 1 << (max_depth - d + min_depth);

        // Launch async task (Backend best practice: utilize available threads)
        tasks.push_back(std::async(std::launch::async, [d, iterations]() {
            int total_check = 0;
            for (int i = 0; i < iterations; ++i) {
                total_check += make_check_deallocate(d);
            }
            return Result{d, iterations, total_check};
        }));
    }

    // Collect and print results in order
    for (auto& task : tasks) {
        Result r = task.get();
        std::cout << r.iterations << "\t trees of depth " << r.depth 
                  << "\t check: " << r.check << std::endl;
    }

    // -----------------------------------------------------------------
    // 5. Check that the long-lived binary tree still exists
    // -----------------------------------------------------------------
    std::cout << "long lived tree of depth " << max_depth 
              << "\t check: " << long_lived_tree->check() << std::endl;

    delete long_lived_tree;

    return 0;
}
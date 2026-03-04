/*
 * Binary Trees Benchmark - C++
 * Uses manual per-node allocation (new/delete).
 * * Compile: g++ -O3 binary_trees.cpp -o binary_trees
 * Usage: ./binary_trees 21
 */

#include <iostream>
#include <cstdlib>

// 1. Define a tree node structure
struct Node {
    Node *left;
    Node *right;

    // Constructor for per-node allocation
    Node(Node* l, Node* r) : left(l), right(r) {}

    // Destructor to recursively deallocate
    ~Node() {
        if (left) delete left;
        if (right) delete right;
    }

    // Walk the tree counting nodes
    int itemCheck() const {
        if (!left) return 1;
        return 1 + left->itemCheck() + right->itemCheck();
    }
};

// Helper to create trees bottom-up
Node* makeTree(int depth) {
    if (depth == 0) {
        // Leaf nodes same allocation as interior
        return new Node(nullptr, nullptr);
    }
    return new Node(makeTree(depth - 1), makeTree(depth - 1));
}

int main(int argc, char* argv[]) {
    int n = (argc > 1) ? std::atoi(argv[1]) : 21;
    int minDepth = 4;
    int maxDepth = (minDepth + 2 > n) ? minDepth + 2 : n;
    int stretchDepth = maxDepth + 1;

    // 2. Allocate "Stretch" Tree
    // Allocation: makeTree uses 'new'
    Node* stretchTree = makeTree(stretchDepth);
    std::cout << "stretch tree of depth " << stretchDepth 
              << "\t check: " << stretchTree->itemCheck() << std::endl;
    
    // Deallocation: uses 'delete'
    delete stretchTree;

    // 3. Allocate Long-Lived Tree
    Node* longLivedTree = makeTree(maxDepth);

    // 4. Allocate, walk, and deallocate many trees
    for (int depth = minDepth; depth <= maxDepth; depth += 2) {
        int iterations = 1 << (maxDepth - depth + minDepth);
        int check = 0;

        for (int i = 1; i <= iterations; ++i) {
            Node* tempTree = makeTree(depth);
            check += tempTree->itemCheck();
            delete tempTree; 
        }

        std::cout << iterations << "\t trees of depth " << depth 
                  << "\t check: " << check << std::endl;
    }

    // 5. Check long-lived tree
    std::cout << "long lived tree of depth " << maxDepth 
              << "\t check: " << longLivedTree->itemCheck() << std::endl;

    // Cleanup long-lived tree
    delete longLivedTree;

    return 0;
}
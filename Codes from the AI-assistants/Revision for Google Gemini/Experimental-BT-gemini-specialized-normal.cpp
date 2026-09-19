#include <iostream>
#include <vector>
#include <chrono>

// 16-byte node on 64-bit systems
struct TreeNode {
    TreeNode* left;
    TreeNode* right;
};

class TreeArena {
private:
    std::vector<TreeNode> arena;
    size_t currentIndex;

public:
    // Pre-allocate the entire capacity required for a perfect tree of depth N
    TreeArena(size_t totalNodes) : currentIndex(0) {
        // reserves memory in one contiguous block, preventing reallocation
        arena.resize(totalNodes); 
    }

    // Allocate a node from the pool in O(1) time
    TreeNode* allocateNode() {
        return &arena[currentIndex++];
    }
};

// Recursive function to build the tree
TreeNode* buildPerfectTree(int depth, TreeArena& arena) {
    TreeNode* node = arena.allocateNode();

    if (depth > 0) {
        node->left = buildPerfectTree(depth - 1, arena);
        node->right = buildPerfectTree(depth - 1, arena);
    } else {
        node->left = nullptr;
        node->right = nullptr;
    }

    return node;
}

int main() {
    // Max safe depth for 8GB RAM is 27
    const int N = 27; 
    
    // Total nodes = 2^(N+1) - 1
    const size_t totalNodes = (1ULL << (N + 1)) - 1; 

    std::cout << "Allocating memory for " << totalNodes << " nodes...\n";
    std::cout << "Estimated memory: " << (totalNodes * sizeof(TreeNode)) / (1024 * 1024 * 1024.0) << " GB\n";

    auto start = std::chrono::high_resolution_clock::now();

    // 1. Initialize the Arena (One single mass-allocation)
    TreeArena arena(totalNodes);

    // 2. Build the Tree
    TreeNode* root = buildPerfectTree(N, arena);

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;

    std::cout << "Perfect binary tree of depth " << N << " built successfully.\n";
    std::cout << "Time elapsed: " << diff.count() << " seconds.\n";

    // Because we used an arena (std::vector), all memory is freed instantly 
    // and cleanly when the 'arena' object goes out of scope here.
    return 0;
}
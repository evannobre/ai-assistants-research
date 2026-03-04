/**
 * Binary Trees Benchmark - C++ Implementation
 * Allocates and deallocates many binary trees using per-node allocation.
 * 
 * Compile: g++ -O3 -o binarytrees binarytrees.cpp
 * Run: ./binarytrees <max_depth>
 * Example: ./binarytrees 21
 */

#include <iostream>
#include <cstdlib>

/**
 * Binary tree node with left and right children.
 * Interior nodes and leaf nodes use the same allocation.
 */
struct TreeNode {
    TreeNode* left;
    TreeNode* right;
    
    TreeNode(TreeNode* l = nullptr, TreeNode* r = nullptr) 
        : left(l), right(r) {}
};

/**
 * Create a binary tree of given depth.
 * Uses per-node allocation with standard new operator.
 * 
 * @param depth The depth of the tree to create
 * @return The root node of the created tree
 */
TreeNode* makeTree(int depth) {
    if (depth > 0) {
        return new TreeNode(
            makeTree(depth - 1),
            makeTree(depth - 1)
        );
    } else {
        return new TreeNode();
    }
}

/**
 * Count nodes in the tree (walk the tree).
 * 
 * @param node The root node to start counting from
 * @return The total number of nodes in the tree
 */
int checkTree(TreeNode* node) {
    if (node->left == nullptr) {
        return 1;
    } else {
        return 1 + checkTree(node->left) + checkTree(node->right);
    }
}

/**
 * Delete a tree and free all its nodes.
 * Uses post-order traversal to properly deallocate all nodes.
 * 
 * @param node The root node of the tree to delete
 */
void deleteTree(TreeNode* node) {
    if (node != nullptr) {
        deleteTree(node->left);
        deleteTree(node->right);
        delete node;
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <max_depth>" << std::endl;
        std::cout << "Example: " << argv[0] << " 21" << std::endl;
        return 1;
    }
    
    int maxDepth = std::atoi(argv[1]);
    int minDepth = 4;
    
    int stretchDepth = maxDepth + 1;
    
    // Stretch memory - allocate and check a large tree, then deallocate it
    {
        TreeNode* stretchTree = makeTree(stretchDepth);
        std::cout << "stretch tree of depth " << stretchDepth 
                  << "\t check: " << checkTree(stretchTree) << std::endl;
        deleteTree(stretchTree);
    }
    
    // Allocate long-lived tree that will survive while other trees are created/destroyed
    TreeNode* longLivedTree = makeTree(maxDepth);
    
    // Allocate, walk, and deallocate many bottom-up binary trees
    for (int depth = minDepth; depth <= maxDepth; depth += 2) {
        int iterations = 1 << (maxDepth - depth + minDepth);
        int checkSum = 0;
        
        for (int i = 0; i < iterations; i++) {
            // Allocate tree
            TreeNode* tempTree = makeTree(depth);
            // Walk tree and count nodes
            checkSum += checkTree(tempTree);
            // Deallocate tree
            deleteTree(tempTree);
        }
        
        std::cout << iterations << "\t trees of depth " << depth 
                  << "\t check: " << checkSum << std::endl;
    }
    
    // Check that long-lived tree still exists
    std::cout << "long lived tree of depth " << maxDepth 
              << "\t check: " << checkTree(longLivedTree) << std::endl;
    
    // Clean up long-lived tree
    deleteTree(longLivedTree);
    
    return 0;
}

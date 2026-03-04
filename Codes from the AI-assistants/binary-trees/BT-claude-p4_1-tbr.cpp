#include <iostream>
#include <memory>
#include <string>
#include <cstdlib>

class TreeNode {
public:
    TreeNode* left;
    TreeNode* right;
    
    TreeNode() : left(nullptr), right(nullptr) {}
    
    ~TreeNode() {
        delete left;
        delete right;
    }
};

TreeNode* makeTree(int depth) {
    TreeNode* node = new TreeNode();
    if (depth > 0) {
        node->left = makeTree(depth - 1);
        node->right = makeTree(depth - 1);
    }
    return node;
}

int checkTree(const TreeNode* node) {
    if (node->left == nullptr) {
        return 1;
    }
    return 1 + checkTree(node->left) + checkTree(node->right);
}

int main(int argc, char* argv[]) {
    int n = (argc > 1) ? std::atoi(argv[1]) : 10;
    
    const int minDepth = 4;
    const int maxDepth = (minDepth + 2 > n) ? minDepth + 2 : n;
    const int stretchDepth = maxDepth + 1;
    
    // Stretch memory
    {
        TreeNode* stretchTree = makeTree(stretchDepth);
        std::cout << "stretch tree of depth " << stretchDepth 
                  << "\t check: " << checkTree(stretchTree) << std::endl;
        delete stretchTree;
    }
    
    // Create long-lived tree
    TreeNode* longLivedTree = makeTree(maxDepth);
    
    // Allocate, walk, and deallocate many bottom-up trees
    for (int depth = minDepth; depth <= maxDepth; depth += 2) {
        const int iterations = 1 << (maxDepth - depth + minDepth);
        int check = 0;
        
        for (int i = 0; i < iterations; ++i) {
            TreeNode* tree = makeTree(depth);
            check += checkTree(tree);
            delete tree;
        }
        
        std::cout << iterations << "\t trees of depth " << depth 
                  << "\t check: " << check << std::endl;
    }
    
    // Check long-lived tree
    std::cout << "long lived tree of depth " << maxDepth 
              << "\t check: " << checkTree(longLivedTree) << std::endl;
    
    delete longLivedTree;
    
    return 0;
}

#include <iostream>
#include <vector>
#include <queue>
#include <memory>
#include <cmath>
#include <cstring>

struct TreeNode {
    int value;
    TreeNode* left;
    TreeNode* right;
    
    TreeNode(int val) : value(val), left(nullptr), right(nullptr) {}
};

class PerfectBinaryTree {
private:
    std::vector<std::unique_ptr<TreeNode>> nodeStorage; // Prevents auto-deletion
    
public:
    TreeNode* createPerfectBinaryTree(int depth) {
        if (depth <= 0) return nullptr;
        
        // Pre-allocate all nodes at once using native memory
        int totalNodes = pow(2, depth) - 1;
        nodeStorage.reserve(totalNodes);
        
        // Create root using explicit allocation
        nodeStorage.push_back(std::make_unique<TreeNode>(1));
        TreeNode* root = nodeStorage.back().get();
        
        std::queue<TreeNode*> currentLevel;
        currentLevel.push(root);
        
        int nodeValue = 2;
        
        // Build tree level by level
        for (int level = 1; level < depth; level++) {
            int levelSize = currentLevel.size();
            
            for (int i = 0; i < levelSize; i++) {
                TreeNode* parent = currentLevel.front();
                currentLevel.pop();
                
                // Create left child
                nodeStorage.push_back(std::make_unique<TreeNode>(nodeValue++));
                parent->left = nodeStorage.back().get();
                currentLevel.push(parent->left);
                
                // Create right child
                nodeStorage.push_back(std::make_unique<TreeNode>(nodeValue++));
                parent->right = nodeStorage.back().get();
                currentLevel.push(parent->right);
            }
        }
        
        // Memory usage report
        size_t memoryUsed = totalNodes * sizeof(TreeNode);
        std::cout << "Memory allocated: " << memoryUsed / (1024 * 1024) 
                  << " MB for " << totalNodes << " nodes" << std::endl;
        
        return root;
    }
    
    // Raw memory allocation alternative
    TreeNode* createWithRawMemory(int depth) {
        if (depth <= 0) return nullptr;
        
        int totalNodes = pow(2, depth) - 1;
        
        // Allocate raw memory block (prevents fragmentation)
        char* memoryBlock = new char[totalNodes * sizeof(TreeNode)];
        TreeNode* nodes = reinterpret_cast<TreeNode*>(memoryBlock);
        
        // Construct nodes in place
        for (int i = 0; i < totalNodes; i++) {
            new (&nodes[i]) TreeNode(i + 1);
        }
        
        // Build tree structure
        for (int i = 0; i < totalNodes / 2; i++) {
            nodes[i].left = &nodes[2 * i + 1];
            nodes[i].right = &nodes[2 * i + 2];
        }
        
        std::cout << "Raw memory allocated: " 
                  << (totalNodes * sizeof(TreeNode)) / (1024 * 1024) 
                  << " MB" << std::endl;
        
        return &nodes[0];
    }
};

int main() {
    PerfectBinaryTree treeBuilder;
    int depth = 20; // ~1 million nodes
    
    std::cout << "Creating perfect binary tree of depth: " << depth << std::endl;
    
    // Method 1: Using managed storage
    TreeNode* tree1 = treeBuilder.createPerfectBinaryTree(depth);
    
    // Method 2: Using raw memory
    TreeNode* tree2 = treeBuilder.createWithRawMemory(depth);
    
    std::cout << "Tree created successfully!" << std::endl;
    
    return 0;
}
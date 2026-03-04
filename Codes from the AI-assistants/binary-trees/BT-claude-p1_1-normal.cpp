#include <iostream>
#include <queue>
#include <memory>
#include <cmath>

struct TreeNode {
    int value;
    int level;
    TreeNode* left;
    TreeNode* right;
    
    TreeNode(int val, int lvl) : value(val), level(lvl), left(nullptr), right(nullptr) {}
};

class BinaryTreeBuilder {
private:
    static int nodeCounter;
    
public:
    static TreeNode* buildPerfectTree(int depth) {
        if (depth < 0) return nullptr;
        
        nodeCounter = 0;
        TreeNode* root = new TreeNode(nodeCounter++, 0);
        
        // Use STL queue for level-order construction
        std::queue<TreeNode*> nodeQueue;
        nodeQueue.push(root);
        
        while (!nodeQueue.empty()) {
            TreeNode* current = nodeQueue.front();
            nodeQueue.pop();
            
            if (current->level < depth) {
                // Allocate left child
                current->left = new TreeNode(nodeCounter++, current->level + 1);
                nodeQueue.push(current->left);
                
                // Allocate right child
                current->right = new TreeNode(nodeCounter++, current->level + 1);
                nodeQueue.push(current->right);
            }
        }
        
        return root;
    }
    
    static void printTreeStats(TreeNode* root, int depth) {
        int expectedNodes = std::pow(2, depth + 1) - 1;
        std::cout << "Tree Statistics:\n";
        std::cout << "Depth: " << depth << "\n";
        std::cout << "Total Nodes Allocated: " << nodeCounter << "\n";
        std::cout << "Expected Nodes: " << expectedNodes << "\n";
    }
    
    static void deleteTree(TreeNode* root) {
        if (!root) return;
        deleteTree(root->left);
        deleteTree(root->right);
        delete root;
    }
};

int BinaryTreeBuilder::nodeCounter = 0;

int main() {
    int depth = 10;
    
    std::cout << "Building perfect binary tree of depth " << depth << "...\n";
    TreeNode* root = BinaryTreeBuilder::buildPerfectTree(depth);
    
    BinaryTreeBuilder::printTreeStats(root, depth);
    
    // Tree exists in memory here - no GC yet
    std::cout << "\nTree built successfully. Memory still allocated.\n";
    
    // Explicit cleanup (simulating pre-GC state)
    BinaryTreeBuilder::deleteTree(root);
    std::cout << "Tree deleted manually.\n";
    
    return 0;
}
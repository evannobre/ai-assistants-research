#include <iostream>
#include <memory>
#include <cmath>
#include <queue>

struct TreeNode {
    std::unique_ptr<TreeNode> left;
    std::unique_ptr<TreeNode> right;
};

std::unique_ptr<TreeNode> create_balanced_tree(int depth) {
    if (depth <= 0) return nullptr;
    
    auto node = std::make_unique<TreeNode>();
    node->left = create_balanced_tree(depth - 1);
    node->right = create_balanced_tree(depth - 1);
    
    return node;
}

int count_nodes(const std::unique_ptr<TreeNode>& root) {
    if (!root) return 0;
    return 1 + count_nodes(root->left) + count_nodes(root->right);
}

void print_tree_structure(const std::unique_ptr<TreeNode>& root, int level = 0) {
    if (!root) return;
    
    std::cout << std::string(level * 2, ' ') << "Node\n";
    print_tree_structure(root->left, level + 1);
    print_tree_structure(root->right, level + 1);
}

int main() {
    int depth = 4;
    auto root = create_balanced_tree(depth);
    
    std::cout << "Created balanced tree with depth " << depth << std::endl;
    std::cout << "Total nodes: " << count_nodes(root) << std::endl;
    std::cout << "Expected nodes: " << (int)std::pow(2, depth) - 1 << std::endl;
    
    std::cout << "\nTree structure:\n";
    print_tree_structure(root);
    
    return 0;
}
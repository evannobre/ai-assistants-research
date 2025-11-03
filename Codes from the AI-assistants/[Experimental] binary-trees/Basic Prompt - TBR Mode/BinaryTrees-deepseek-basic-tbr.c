#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct TreeNode {
    struct TreeNode* left;
    struct TreeNode* right;
} TreeNode;

TreeNode* create_balanced_tree(int depth) {
    if (depth <= 0) return NULL;
    
    TreeNode* node = (TreeNode*)malloc(sizeof(TreeNode));
    if (!node) return NULL;
    
    node->left = create_balanced_tree(depth - 1);
    node->right = create_balanced_tree(depth - 1);
    
    return node;
}

void free_tree(TreeNode* root) {
    if (!root) return;
    free_tree(root->left);
    free_tree(root->right);
    free(root);
}

int count_nodes(TreeNode* root) {
    if (!root) return 0;
    return 1 + count_nodes(root->left) + count_nodes(root->right);
}

int main() {
    int depth = 4;
    TreeNode* root = create_balanced_tree(depth);
    
    printf("Created balanced tree with depth %d\n", depth);
    printf("Total nodes: %d\n", count_nodes(root));
    printf("Expected nodes: %d\n", (int)pow(2, depth) - 1);
    
    free_tree(root);
    return 0;
}
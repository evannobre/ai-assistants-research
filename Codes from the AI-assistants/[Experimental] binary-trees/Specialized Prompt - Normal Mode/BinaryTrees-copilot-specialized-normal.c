#include <stdio.h>
#include <stdlib.h>

// Define the tree node structure without any value
typedef struct TreeNode {
    struct TreeNode* left;
    struct TreeNode* right;
} TreeNode;

// Recursively allocate memory for a perfect binary tree of given depth
TreeNode* createPerfectTree(int depth) {
    if (depth <= 0) return NULL;

    TreeNode* node = (TreeNode*)malloc(sizeof(TreeNode));
    if (!node) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }

    node->left = createPerfectTree(depth - 1);
    node->right = createPerfectTree(depth - 1);

    return node;
}

// Recursively free the tree memory
void freeTree(TreeNode* root) {
    if (!root) return;
    freeTree(root->left);
    freeTree(root->right);
    free(root);
}

// Entry point
int main() {
    int depth = 4; // Example: depth 4 → 15 nodes
    TreeNode* root = createPerfectTree(depth);

    printf("Perfect binary tree of depth %d created.\n", depth);

    // Clean up
    freeTree(root);
    printf("Memory freed.\n");

    return 0;
}
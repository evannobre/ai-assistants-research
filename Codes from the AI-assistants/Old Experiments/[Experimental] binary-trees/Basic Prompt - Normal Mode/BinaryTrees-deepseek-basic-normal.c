#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct TreeNode {
    struct TreeNode* left;
    struct TreeNode* right;
} TreeNode;

// Calculate height of perfect binary tree for given number of nodes
int calculate_height(int total_nodes) {
    return (int)log2(total_nodes + 1);
}

// Create perfect balanced binary tree using memory allocation only
TreeNode* create_perfect_balanced_tree(int height) {
    if (height <= 0) {
        return NULL;
    }
    
    TreeNode* node = (TreeNode*)malloc(sizeof(TreeNode));
    if (node == NULL) {
        return NULL;
    }
    
    // Memory allocation serves as our "creation" mechanism
    node->left = create_perfect_balanced_tree(height - 1);
    node->right = create_perfect_balanced_tree(height - 1);
    
    return node;
}

// Traverse and verify structure without storing values
void traverse_structure(TreeNode* root, int depth) {
    if (root == NULL) {
        return;
    }
    
    // Print memory addresses to demonstrate structure
    printf("Node at depth %d: %p\n", depth, (void*)root);
    printf("  Left: %p, Right: %p\n", 
           (void*)root->left, (void*)root->right);
    
    traverse_structure(root->left, depth + 1);
    traverse_structure(root->right, depth + 1);
}

// Count nodes to verify perfect tree structure
int count_nodes(TreeNode* root) {
    if (root == NULL) {
        return 0;
    }
    return 1 + count_nodes(root->left) + count_nodes(root->right);
}

// Free allocated memory
void free_tree(TreeNode* root) {
    if (root == NULL) {
        return;
    }
    free_tree(root->left);
    free_tree(root->right);
    free(root);
}

int main() {
    int height = 3; // Creates 2^3 - 1 = 7 nodes
    
    printf("Creating perfect balanced binary tree with height %d\n", height);
    
    TreeNode* root = create_perfect_balanced_tree(height);
    
    if (root == NULL) {
        printf("Memory allocation failed!\n");
        return 1;
    }
    
    printf("\nTree Structure (memory addresses):\n");
    traverse_structure(root, 0);
    
    int node_count = count_nodes(root);
    printf("\nTotal nodes created: %d\n", node_count);
    printf("Expected nodes for height %d: %d\n", height, (1 << height) - 1);
    
    // Verify perfect balance
    if (node_count == (1 << height) - 1) {
        printf("✓ Perfect balanced tree verified!\n");
    } else {
        printf("✗ Tree structure incorrect!\n");
    }
    
    free_tree(root);
    return 0;
}
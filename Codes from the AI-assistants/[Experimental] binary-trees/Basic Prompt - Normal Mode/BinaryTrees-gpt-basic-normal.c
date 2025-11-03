#include <stdio.h>
#include <stdlib.h>

// Define a tree node with no value payload
typedef struct Node {
    struct Node* left;
    struct Node* right;
} Node;

// Function to create a new empty node
Node* create_node() {
    Node* node = (Node*) malloc(sizeof(Node));
    if (node == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(EXIT_FAILURE);
    }
    node->left = NULL;
    node->right = NULL;
    return node;
}

// Recursive function to build a perfect balanced tree of given depth
Node* build_perfect_tree(int depth) {
    if (depth <= 0) {
        return NULL;
    }

    Node* root = create_node();
    root->left  = build_perfect_tree(depth - 1);
    root->right = build_perfect_tree(depth - 1);
    return root;
}

// Function to free the allocated memory
void free_tree(Node* root) {
    if (root == NULL) return;
    free_tree(root->left);
    free_tree(root->right);
    free(root);
}

// Utility: Count total nodes in the tree
int count_nodes(Node* root) {
    if (root == NULL) return 0;
    return 1 + count_nodes(root->left) + count_nodes(root->right);
}

int main() {
    int depth = 4;  // Example: create a perfect tree of depth 4
    Node* root = build_perfect_tree(depth);

    printf("Perfect binary tree of depth %d created.\n", depth);
    printf("Total nodes: %d\n", count_nodes(root));

    free_tree(root);
    return 0;
}

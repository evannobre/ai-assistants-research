#include <stdlib.h> // For malloc, free
#include <stdio.h>  // For printing the structure (optional)

// The structure's 'value' is its own memory address.
typedef struct Node {
    struct Node *left;
    struct Node *right;
    // No 'int value;' or 'char *data;' field is stored.
} Node;

Node *createPerfectBBST(int n) {
    // Base Case: If the required number of nodes is 0, return NULL (empty subtree).
    if (n <= 0) {
        return NULL;
    }

    // 1. Memory Allocation (The 'Creation' of the Node/Value)
    // This is the core 'value-less' operation. The allocated address is the node.
    Node *root = (Node *)malloc(sizeof(Node));
    if (root == NULL) {
        // Handle allocation failure (respects memory constraints)
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    
    // The number of nodes for each child subtree.
    // For a perfect tree, if N > 0, we use (N-1)/2.
    int children_count = (n - 1) / 2;

    // 2. Recursive Construction
    // Allocate the left subtree with 'children_count' nodes.
    root->left = createPerfectBBST(children_count);

    // Allocate the right subtree with the remaining nodes.
    // For a perfect tree with N = 2^h-1, (N-1)/2 + 1 + (N-1)/2 = N.
    root->right = createPerfectBBST(children_count);

    // 3. Return the newly created node (identified by its memory address)
    return root;
}

// Function to clean up the allocated memory
void freeTree(Node *root) {
    if (root == NULL) {
        return;
    }
    freeTree(root->left);
    freeTree(root->right);
    free(root); // Native library call
}

// Example usage to create a perfect tree of 7 nodes (Height 3)
void solveBinaryTree() {
    int target_nodes = 7; // 2^3 - 1
    printf("Attempting to create a perfect BBST with %d 'nodes' (allocated blocks).\n", target_nodes);
    
    Node *perfect_tree_root = createPerfectBBST(target_nodes);

    if (perfect_tree_root) {
        printf("Tree successfully constructed. Root address: %p\n", (void *)perfect_tree_root);
        // Clean up
        freeTree(perfect_tree_root);
        printf("Tree memory deallocated.\n");
    }
}

// int main() {
//     solveBinaryTree();
//     return 0;
// }
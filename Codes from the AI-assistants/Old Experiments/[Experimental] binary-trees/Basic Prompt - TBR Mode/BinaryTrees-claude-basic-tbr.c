#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/**
 * Memory-Based Perfect Balanced Binary Tree
 * 
 * This algorithm uses memory allocation as the primary data structure mechanism.
 * Instead of storing values in nodes, we use the memory addresses themselves
 * to represent the tree structure. The allocation pattern creates a perfect
 * balanced binary tree.
 */

typedef struct TreeNode {
    struct TreeNode *left;
    struct TreeNode *right;
    void *mem_address;  // The allocated memory block address serves as the identifier
} TreeNode;

/**
 * Calculate the height needed for n nodes in a perfect binary tree
 */
int calculate_height(int n) {
    if (n <= 0) return 0;
    return (int)ceil(log2(n + 1));
}

/**
 * Calculate total nodes in a perfect binary tree of given height
 */
int perfect_tree_nodes(int height) {
    return (1 << height) - 1;  // 2^height - 1
}

/**
 * Allocate a tree node and a memory block (without storing values)
 * The memory block allocation itself represents the node's existence
 */
TreeNode* allocate_node(size_t block_size) {
    TreeNode *node = (TreeNode*)malloc(sizeof(TreeNode));
    if (!node) return NULL;
    
    // Allocate a memory block - the address itself is the "value"
    node->mem_address = malloc(block_size);
    if (!node->mem_address) {
        free(node);
        return NULL;
    }
    
    node->left = NULL;
    node->right = NULL;
    
    return node;
}

/**
 * Build a perfect balanced binary tree using memory allocation
 * Uses level-order (breadth-first) approach to ensure perfect balance
 */
TreeNode* build_perfect_tree(int total_nodes, size_t block_size) {
    if (total_nodes <= 0) return NULL;
    
    // Create root
    TreeNode *root = allocate_node(block_size);
    if (!root) return NULL;
    
    // Use array-based queue for level-order construction
    TreeNode **queue = (TreeNode**)malloc(sizeof(TreeNode*) * total_nodes);
    if (!queue) {
        free(root->mem_address);
        free(root);
        return NULL;
    }
    
    int front = 0, rear = 0;
    queue[rear++] = root;
    int nodes_created = 1;
    
    // Build tree level by level
    while (front < rear && nodes_created < total_nodes) {
        TreeNode *current = queue[front++];
        
        // Create left child
        if (nodes_created < total_nodes) {
            current->left = allocate_node(block_size);
            if (!current->left) break;
            queue[rear++] = current->left;
            nodes_created++;
        }
        
        // Create right child
        if (nodes_created < total_nodes) {
            current->right = allocate_node(block_size);
            if (!current->right) break;
            queue[rear++] = current->right;
            nodes_created++;
        }
    }
    
    free(queue);
    return root;
}

/**
 * Build perfect tree using recursive approach (alternative method)
 */
TreeNode* build_perfect_tree_recursive(int height, size_t block_size) {
    if (height <= 0) return NULL;
    
    TreeNode *node = allocate_node(block_size);
    if (!node) return NULL;
    
    if (height > 1) {
        node->left = build_perfect_tree_recursive(height - 1, block_size);
        node->right = build_perfect_tree_recursive(height - 1, block_size);
    }
    
    return node;
}

/**
 * Traverse tree in-order and print memory addresses
 */
void inorder_traversal(TreeNode *node, int *count) {
    if (!node) return;
    
    inorder_traversal(node->left, count);
    printf("Node %d: Memory Address = %p\n", ++(*count), node->mem_address);
    inorder_traversal(node->right, count);
}

/**
 * Calculate tree height
 */
int tree_height(TreeNode *node) {
    if (!node) return 0;
    
    int left_height = tree_height(node->left);
    int right_height = tree_height(node->right);
    
    return 1 + (left_height > right_height ? left_height : right_height);
}

/**
 * Count total nodes in tree
 */
int count_nodes(TreeNode *node) {
    if (!node) return 0;
    return 1 + count_nodes(node->left) + count_nodes(node->right);
}

/**
 * Verify if tree is perfectly balanced
 */
int is_perfect_balanced(TreeNode *node, int depth, int level) {
    if (!node) return (depth == level);
    
    if (!node->left && !node->right) return (depth == level);
    
    if (!node->left || !node->right) return 0;
    
    return is_perfect_balanced(node->left, depth, level + 1) &&
           is_perfect_balanced(node->right, depth, level + 1);
}

/**
 * Free all allocated memory
 */
void free_tree(TreeNode *node) {
    if (!node) return;
    
    free_tree(node->left);
    free_tree(node->right);
    free(node->mem_address);  // Free the allocated memory block
    free(node);
}

/**
 * Print tree structure (level-order)
 */
void print_tree_structure(TreeNode *root) {
    if (!root) return;
    
    int h = tree_height(root);
    int max_nodes = (1 << h) - 1;
    
    TreeNode **queue = (TreeNode**)calloc(max_nodes, sizeof(TreeNode*));
    int front = 0, rear = 0;
    
    queue[rear++] = root;
    
    printf("\nTree Structure (Level-order):\n");
    int level = 0, level_nodes = 1, current_level_count = 0;
    
    while (front < rear) {
        TreeNode *current = queue[front++];
        
        if (current_level_count == 0) {
            printf("Level %d: ", level++);
        }
        
        if (current) {
            printf("[%p] ", current->mem_address);
            if (rear < max_nodes) queue[rear++] = current->left;
            if (rear < max_nodes) queue[rear++] = current->right;
        } else {
            printf("[NULL] ");
        }
        
        current_level_count++;
        if (current_level_count == level_nodes) {
            printf("\n");
            current_level_count = 0;
            level_nodes *= 2;
        }
    }
    
    free(queue);
}

int main() {
    printf("=== Memory-Based Perfect Balanced Binary Tree ===\n\n");
    
    int num_nodes = 15;  // Creates a perfect tree of height 4
    size_t block_size = 64;  // Size of memory blocks to allocate
    
    printf("Creating perfect balanced tree with %d nodes...\n", num_nodes);
    printf("Block size for each node: %zu bytes\n\n", block_size);
    
    // Build the tree using iterative approach
    TreeNode *root = build_perfect_tree(num_nodes, block_size);
    
    if (!root) {
        printf("Failed to create tree!\n");
        return 1;
    }
    
    // Display tree statistics
    int height = tree_height(root);
    int total = count_nodes(root);
    int expected_height = calculate_height(num_nodes);
    
    printf("Tree Statistics:\n");
    printf("- Total nodes: %d\n", total);
    printf("- Tree height: %d\n", height);
    printf("- Expected height: %d\n", expected_height);
    printf("- Is perfectly balanced: %s\n\n", 
           is_perfect_balanced(root, height, 1) ? "Yes" : "No");
    
    // Print tree structure
    print_tree_structure(root);
    
    // In-order traversal showing memory addresses
    printf("\nIn-order Traversal (Memory Addresses):\n");
    int count = 0;
    inorder_traversal(root, &count);
    
    // Clean up
    printf("\nFreeing allocated memory...\n");
    free_tree(root);
    printf("Done!\n");
    
    return 0;
}
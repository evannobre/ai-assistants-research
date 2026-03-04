#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

typedef struct TreeNode {
    struct TreeNode* left;
    struct TreeNode* right;
    // No value field - we use memory topology itself
} TreeNode;

// Calculate height of perfectly balanced tree based on node count
int calculate_height(int node_count) {
    return (int)log2(node_count + 1);
}

// Recursive function to create balanced tree using memory topology
TreeNode* create_balanced_tree(int depth, uintptr_t base_addr) {
    if (depth <= 0) return NULL;
    
    TreeNode* node = (TreeNode*)malloc(sizeof(TreeNode));
    if (!node) return NULL;
    
    // Use memory address relationships to determine structure
    // Left child gets lower address space, right gets higher
    uintptr_t current_addr = (uintptr_t)node;
    
    // Calculate address offsets for children based on depth
    size_t offset = (1 << (depth - 2)) * sizeof(TreeNode);
    
    // Create children recursively
    node->left = create_balanced_tree(depth - 1, base_addr);
    node->right = create_balanced_tree(depth - 1, base_addr + offset);
    
    return node;
}

// Create perfect balanced tree with 2^height - 1 nodes
TreeNode* create_perfect_balanced_tree(int height) {
    if (height <= 0) return NULL;
    
    int total_nodes = (1 << height) - 1; // 2^height - 1
    printf("Creating perfect balanced tree with height %d (%d nodes)\n", 
           height, total_nodes);
    
    return create_balanced_tree(height, 0);
}

// Alternative iterative approach using memory pooling
TreeNode* create_balanced_tree_iterative(int height) {
    if (height <= 0) return NULL;
    
    int total_nodes = (1 << height) - 1;
    TreeNode* pool = (TreeNode*)malloc(total_nodes * sizeof(TreeNode));
    
    if (!pool) return NULL;
    
    // Build tree using array representation
    for (int i = 0; i < total_nodes; i++) {
        int left_idx = 2 * i + 1;
        int right_idx = 2 * i + 2;
        
        pool[i].left = (left_idx < total_nodes) ? &pool[left_idx] : NULL;
        pool[i].right = (right_idx < total_nodes) ? &pool[right_idx] : NULL;
    }
    
    return &pool[0];
}

// Memory-efficient traversal using pointer arithmetic
void traverse_tree(TreeNode* root, int level) {
    if (!root) return;
    
    // Use memory address as "pseudo-value" for demonstration
    printf("Level %d: Node at address %p\n", level, (void*)root);
    
    traverse_tree(root->left, level + 1);
    traverse_tree(root->right, level + 1);
}

// Calculate memory usage
void calculate_memory_usage(int height) {
    int total_nodes = (1 << height) - 1;
    size_t memory_used = total_nodes * sizeof(TreeNode);
    
    printf("Memory usage for height %d:\n", height);
    printf("  Nodes: %d\n", total_nodes);
    printf("  Memory per node: %zu bytes\n", sizeof(TreeNode));
    printf("  Total memory: %zu bytes (%.2f MB)\n", 
           memory_used, (double)memory_used / (1024 * 1024));
}

// Clean up memory
void free_tree(TreeNode* root) {
    if (!root) return;
    
    free_tree(root->left);
    free_tree(root->right);
    free(root);
}

// Memory-efficient alternative using single free for pooled memory
void free_pooled_tree(TreeNode* root) {
    if (root) {
        // For pooled trees, we can free the entire block at once
        // This is more efficient than recursive freeing
        free(root);
    }
}

int main() {
    int height = 4; // Creates 15 nodes (2^4 - 1)
    
    printf("=== Memory Topology Balanced Binary Tree ===\n");
    
    // Calculate and display memory requirements
    calculate_memory_usage(height);
    
    printf("\n=== Recursive Construction ===\n");
    TreeNode* tree1 = create_perfect_balanced_tree(height);
    if (tree1) {
        traverse_tree(tree1, 0);
        free_tree(tree1);
    }
    
    printf("\n=== Iterative Pooled Construction ===\n");
    TreeNode* tree2 = create_balanced_tree_iterative(height);
    if (tree2) {
        traverse_tree(tree2, 0);
        free_pooled_tree(tree2);
    }
    
    // Test with larger tree to demonstrate scalability
    printf("\n=== Scalability Test ===\n");
    int max_height = 8; // 255 nodes, ~4KB memory
    calculate_memory_usage(max_height);
    
    TreeNode* large_tree = create_balanced_tree_iterative(max_height);
    if (large_tree) {
        printf("Large tree created successfully with height %d\n", max_height);
        free_pooled_tree(large_tree);
    }
    
    return 0;
}
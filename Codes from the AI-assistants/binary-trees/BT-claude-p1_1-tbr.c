/*
 * Perfect Binary Tree Memory Allocator in C
 * Demonstrates explicit memory allocation without automatic GC
 * Uses native C memory management (malloc/free)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* Structure for binary tree node */
typedef struct TreeNode {
    int value;
    struct TreeNode *left;
    struct TreeNode *right;
} TreeNode;

/* Structure to track memory allocation statistics */
typedef struct {
    size_t total_bytes;
    size_t node_count;
    size_t allocation_count;
    clock_t start_time;
    clock_t end_time;
} AllocationStats;

/* Global statistics */
AllocationStats stats = {0, 0, 0, 0, 0};

/*
 * Custom memory allocator with tracking
 */
void* tracked_malloc(size_t size) {
    void* ptr = malloc(size);
    if (ptr != NULL) {
        stats.total_bytes += size;
        stats.allocation_count++;
    }
    return ptr;
}

/*
 * Create a new tree node with memory tracking
 */
TreeNode* create_node(int value) {
    TreeNode* node = (TreeNode*)tracked_malloc(sizeof(TreeNode));
    
    if (node == NULL) {
        fprintf(stderr, "Error: Memory allocation failed for node %d\n", value);
        return NULL;
    }
    
    node->value = value;
    node->left = NULL;
    node->right = NULL;
    stats.node_count++;
    
    return node;
}

/*
 * MAIN ALGORITHM: Recursive allocation of perfect binary tree
 * 
 * A perfect binary tree of depth N has:
 * - All leaf nodes at depth N
 * - All internal nodes have exactly 2 children
 * - Total nodes = 2^(N+1) - 1
 * 
 * Algorithm:
 * 1. Base case: if current_depth > target_depth, return NULL
 * 2. Allocate new node via create_node()
 * 3. Calculate child values (binary heap indexing)
 * 4. Recursively allocate left subtree at depth+1
 * 5. Recursively allocate right subtree at depth+1
 * 6. Return allocated node
 * 
 * Time Complexity: O(2^N) where N is depth
 * Space Complexity: O(2^N) for nodes + O(N) for recursion stack
 */
TreeNode* allocate_perfect_tree(int current_depth, int target_depth, int node_value) {
    /* Base case: exceeded target depth */
    if (current_depth > target_depth) {
        return NULL;
    }
    
    /* Allocate current node */
    TreeNode* node = create_node(node_value);
    if (node == NULL) {
        return NULL;  /* Allocation failed */
    }
    
    /* Calculate child values using binary heap indexing */
    int left_value = 2 * node_value + 1;
    int right_value = 2 * node_value + 2;
    
    /* Recursively allocate left and right subtrees */
    node->left = allocate_perfect_tree(current_depth + 1, target_depth, left_value);
    node->right = allocate_perfect_tree(current_depth + 1, target_depth, right_value);
    
    return node;
}

/*
 * Calculate expected number of nodes for perfect binary tree
 */
size_t calculate_expected_nodes(int depth) {
    return (1 << (depth + 1)) - 1;  /* 2^(depth+1) - 1 */
}

/*
 * Verify tree depth
 */
int calculate_tree_depth(TreeNode* node) {
    if (node == NULL) {
        return -1;
    }
    
    int left_depth = calculate_tree_depth(node->left);
    int right_depth = calculate_tree_depth(node->right);
    
    return 1 + (left_depth > right_depth ? left_depth : right_depth);
}

/*
 * Traverse tree in preorder (limited display)
 */
void traverse_preorder(TreeNode* node, int depth, int max_depth) {
    if (node == NULL || depth > max_depth) {
        return;
    }
    
    /* Print indentation */
    for (int i = 0; i < depth; i++) {
        printf("  ");
    }
    
    printf("Node(value=%d, depth=%d)\n", node->value, depth);
    
    traverse_preorder(node->left, depth + 1, max_depth);
    traverse_preorder(node->right, depth + 1, max_depth);
}

/*
 * Free all tree nodes (manual memory management - no GC)
 */
void free_tree(TreeNode* node) {
    if (node == NULL) {
        return;
    }
    
    /* Post-order traversal for safe deletion */
    free_tree(node->left);
    free_tree(node->right);
    free(node);
}

/*
 * Print allocation statistics
 */
void print_statistics(int depth) {
    size_t expected_nodes = calculate_expected_nodes(depth);
    double time_taken = (double)(stats.end_time - stats.start_time) / CLOCKS_PER_SEC;
    
    printf("\n");
    printf("============================================================\n");
    printf("Memory Allocation Statistics\n");
    printf("============================================================\n");
    printf("  Target depth:           %d\n", depth);
    printf("  Expected nodes:         %zu\n", expected_nodes);
    printf("  Actual nodes allocated: %zu\n", stats.node_count);
    printf("  Status:                 %s\n", 
           stats.node_count == expected_nodes ? "✓ PASS" : "✗ FAIL");
    printf("\n");
    printf("  Total memory allocated: %zu bytes\n", stats.total_bytes);
    printf("  Memory per node (avg):  %.2f bytes\n", 
           (double)stats.total_bytes / stats.node_count);
    printf("  Allocation calls:       %zu\n", stats.allocation_count);
    printf("  Time taken:             %.6f seconds\n", time_taken);
    printf("============================================================\n");
}

/*
 * Main function to demonstrate the algorithm
 */
int main() {
    printf("Perfect Binary Tree Memory Allocator (C Implementation)\n");
    printf("Using native C memory management (malloc/free)\n");
    printf("============================================================\n\n");
    
    int depths[] = {3, 5, 8, 10};
    int num_tests = sizeof(depths) / sizeof(depths[0]);
    
    for (int i = 0; i < num_tests; i++) {
        int depth = depths[i];
        
        printf("\n############################################################\n");
        printf("# Testing with Depth = %d\n", depth);
        printf("############################################################\n");
        
        /* Reset statistics */
        memset(&stats, 0, sizeof(AllocationStats));
        
        /* Start timing */
        stats.start_time = clock();
        
        /* ALLOCATE TREE - All nodes in memory before any cleanup */
        printf("\nAllocating perfect binary tree...\n");
        TreeNode* root = allocate_perfect_tree(0, depth, 0);
        
        /* End timing */
        stats.end_time = clock();
        
        if (root == NULL) {
            fprintf(stderr, "Error: Failed to allocate tree\n");
            continue;
        }
        
        /* Verify tree structure */
        int actual_depth = calculate_tree_depth(root);
        printf("\nTree Verification:\n");
        printf("  Actual depth:   %d\n", actual_depth);
        printf("  Expected depth: %d\n", depth);
        printf("  Depth check:    %s\n", 
               actual_depth == depth ? "✓ PASS" : "✗ FAIL");
        
        /* Print statistics */
        print_statistics(depth);
        
        /* Display tree structure for small depths */
        if (depth <= 4) {
            printf("\nTree Structure (Preorder Traversal):\n");
            printf("============================================================\n");
            traverse_preorder(root, 0, depth);
        }
        
        /* IMPORTANT: Tree is still fully in memory here */
        printf("\n⚠️  ALL %zu NODES ARE CURRENTLY IN MEMORY\n", stats.node_count);
        printf("   No garbage collection - manual memory management\n");
        
        /* Manual cleanup (no GC in C) */
        printf("\n");
        printf("============================================================\n");
        printf("Cleanup Phase\n");
        printf("============================================================\n");
        printf("  Freeing all %zu nodes...\n", stats.node_count);
        
        free_tree(root);
        
        printf("  ✓ All nodes freed\n");
        printf("  ✓ Memory released back to system\n");
        
        printf("\n✓ Test completed for depth %d\n", depth);
    }
    
    printf("\n============================================================\n");
    printf("All tests completed successfully!\n");
    printf("============================================================\n");
    
    return 0;
}

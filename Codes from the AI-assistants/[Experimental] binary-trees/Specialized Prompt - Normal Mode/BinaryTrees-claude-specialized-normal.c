/*
 * Perfect Balanced Binary Tree using Memory Allocation
 * Memory addresses encode tree structure without storing values
 * Optimized for: Ubuntu 24.04.4, 8GB RAM, 256GB SSD
 * Compile: gcc -O3 -o tree perfect_tree.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <sys/resource.h>

// Configuration based on system specs
#define MAX_RAM_GB 8
#define SAFETY_MARGIN 0.7  // Use 70% of available RAM
#define NODE_SIZE sizeof(TreeNode)

typedef struct TreeNode {
    struct TreeNode *left;
    struct TreeNode *right;
    // No data field - the memory address IS the identifier
} TreeNode;

typedef struct {
    TreeNode *nodes;
    size_t capacity;
    size_t size;
    uintptr_t base_addr;
} TreeAllocator;

// Calculate maximum tree height based on available memory
size_t calculate_max_height() {
    struct rlimit rl;
    getrlimit(RLIMIT_AS, &rl);
    
    size_t available_mem = (size_t)(MAX_RAM_GB * 1024ULL * 1024ULL * 1024ULL * SAFETY_MARGIN);
    size_t max_nodes = available_mem / NODE_SIZE;
    
    // Perfect tree: nodes = 2^(h+1) - 1
    size_t height = (size_t)(log2(max_nodes + 1)) - 1;
    
    printf("Available memory: %.2f GB\n", available_mem / (1024.0 * 1024.0 * 1024.0));
    printf("Max nodes: %zu\n", max_nodes);
    printf("Recommended max height: %zu\n", height);
    
    return height;
}

// Initialize tree allocator
TreeAllocator* init_allocator(size_t height) {
    TreeAllocator *alloc = (TreeAllocator*)malloc(sizeof(TreeAllocator));
    if (!alloc) return NULL;
    
    // Perfect binary tree has 2^(h+1) - 1 nodes
    alloc->capacity = (1ULL << (height + 1)) - 1;
    alloc->size = 0;
    
    // Allocate contiguous memory block
    alloc->nodes = (TreeNode*)calloc(alloc->capacity, NODE_SIZE);
    if (!alloc->nodes) {
        free(alloc);
        return NULL;
    }
    
    alloc->base_addr = (uintptr_t)alloc->nodes;
    
    printf("Allocated %zu nodes (%.2f MB)\n", 
           alloc->capacity, 
           (alloc->capacity * NODE_SIZE) / (1024.0 * 1024.0));
    
    return alloc;
}

// Get node index from memory address
static inline size_t get_node_index(TreeAllocator *alloc, TreeNode *node) {
    return ((uintptr_t)node - alloc->base_addr) / NODE_SIZE;
}

// Get node pointer from index
static inline TreeNode* get_node_ptr(TreeAllocator *alloc, size_t idx) {
    return (idx < alloc->capacity) ? &alloc->nodes[idx] : NULL;
}

// Build perfect balanced tree using array-based indexing
void build_perfect_tree(TreeAllocator *alloc, size_t height) {
    size_t total_nodes = (1ULL << (height + 1)) - 1;
    
    printf("Building perfect tree with height %zu (%zu nodes)...\n", 
           height, total_nodes);
    
    // Build tree level by level
    for (size_t i = 0; i < total_nodes; i++) {
        size_t left_idx = 2 * i + 1;
        size_t right_idx = 2 * i + 2;
        
        // Set children pointers if within bounds
        if (left_idx < total_nodes) {
            alloc->nodes[i].left = &alloc->nodes[left_idx];
        } else {
            alloc->nodes[i].left = NULL;
        }
        
        if (right_idx < total_nodes) {
            alloc->nodes[i].right = &alloc->nodes[right_idx];
        } else {
            alloc->nodes[i].right = NULL;
        }
    }
    
    alloc->size = total_nodes;
    printf("Tree construction complete!\n");
}

// Verify tree balance using address-based traversal
int verify_balance(TreeNode *node, TreeAllocator *alloc) {
    if (!node) return 0;
    
    int left_height = verify_balance(node->left, alloc);
    int right_height = verify_balance(node->right, alloc);
    
    if (left_height == -1 || right_height == -1) return -1;
    if (abs(left_height - right_height) > 1) return -1;
    
    return 1 + (left_height > right_height ? left_height : right_height);
}

// In-order traversal using memory addresses
void inorder_traversal(TreeNode *node, TreeAllocator *alloc, size_t *count, size_t limit) {
    if (!node || *count >= limit) return;
    
    inorder_traversal(node->left, alloc, count, limit);
    
    if (*count < limit) {
        // Use memory address as node identifier
        size_t idx = get_node_index(alloc, node);
        printf("Node[%zu] @ %p\n", idx, (void*)node);
        (*count)++;
    }
    
    inorder_traversal(node->right, alloc, count, limit);
}

// Level-order traversal (BFS) using array indexing
void levelorder_traversal(TreeAllocator *alloc, size_t limit) {
    printf("\nLevel-order traversal (first %zu nodes):\n", limit);
    
    size_t count = 0;
    for (size_t i = 0; i < alloc->size && count < limit; i++) {
        printf("Node[%zu] @ %p | Left: %p | Right: %p\n",
               i,
               (void*)&alloc->nodes[i],
               (void*)alloc->nodes[i].left,
               (void*)alloc->nodes[i].right);
        count++;
    }
}

// Get tree statistics
void print_statistics(TreeAllocator *alloc, size_t height) {
    printf("\n=== Tree Statistics ===\n");
    printf("Height: %zu\n", height);
    printf("Total nodes: %zu\n", alloc->size);
    printf("Memory used: %.2f MB\n", 
           (alloc->size * NODE_SIZE) / (1024.0 * 1024.0));
    printf("Leaf nodes: %zu\n", 1ULL << height);
    printf("Internal nodes: %zu\n", alloc->size - (1ULL << height));
    printf("Base address: %p\n", (void*)alloc->base_addr);
    printf("Address range: %p - %p\n", 
           (void*)alloc->base_addr,
           (void*)(alloc->base_addr + alloc->size * NODE_SIZE));
}

// Cleanup
void destroy_allocator(TreeAllocator *alloc) {
    if (alloc) {
        if (alloc->nodes) free(alloc->nodes);
        free(alloc);
    }
}

int main(int argc, char *argv[]) {
    printf("=== Perfect Balanced Binary Tree ===\n");
    printf("System: Ubuntu 24.04.4 64-bit | RAM: 8GB | SSD: 256GB\n\n");
    
    // Determine optimal height
    size_t max_height = calculate_max_height();
    size_t height = (argc > 1) ? atoi(argv[1]) : 10;
    
    if (height > max_height) {
        printf("Warning: Height %zu exceeds safe limit %zu. Using %zu.\n", 
               height, max_height, max_height);
        height = max_height;
    }
    
    // Initialize allocator
    TreeAllocator *alloc = init_allocator(height);
    if (!alloc) {
        fprintf(stderr, "Failed to initialize allocator\n");
        return 1;
    }
    
    // Build perfect balanced tree
    build_perfect_tree(alloc, height);
    
    // Verify balance
    TreeNode *root = get_node_ptr(alloc, 0);
    int tree_height = verify_balance(root, alloc);
    printf("\nVerified tree height: %d\n", tree_height);
    printf("Tree is %s\n", (tree_height == (int)height) ? "BALANCED ✓" : "UNBALANCED ✗");
    
    // Print statistics
    print_statistics(alloc, height);
    
    // Sample traversals (limited output)
    printf("\n=== Sample Traversals (first 10 nodes) ===\n");
    printf("\nIn-order:\n");
    size_t count = 0;
    inorder_traversal(root, alloc, &count, 10);
    
    levelorder_traversal(alloc, 10);
    
    // Cleanup
    destroy_allocator(alloc);
    printf("\nMemory freed successfully.\n");
    
    return 0;
}
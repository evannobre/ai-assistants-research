#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct Node {
    int id;
    struct Node* left;
    struct Node* right;
} Node;

Node* build_perfect_binary_tree(int depth) {
    if (depth <= 0) return NULL;
    
    int total_nodes = (1 << depth) - 1;  // 2^depth - 1
    
    // Use calloc for zero-initialized contiguous memory
    Node* memory_pool = (Node*)calloc(total_nodes, sizeof(Node));
    
    // Create root
    Node* root = &memory_pool[0];
    root->id = 0;
    
    // Use array-based level order construction
    for (int i = 0; i < total_nodes; i++) {
        int left_idx = 2 * i + 1;
        int right_idx = 2 * i + 2;
        
        if (left_idx < total_nodes) {
            memory_pool[i].left = &memory_pool[left_idx];
            memory_pool[left_idx].id = left_idx;
        }
        if (right_idx < total_nodes) {
            memory_pool[i].right = &memory_pool[right_idx];
            memory_pool[right_idx].id = right_idx;
        }
    }
    
    return root;
}
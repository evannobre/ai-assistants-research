/*
 * Perfect Binary Tree with Explicit Memory Allocation in C
 * Author: Computer Scientist specializing in back-end development
 * Target: Ubuntu 24.04.4 64-bit, 8GB RAM, 256GB SSD
 * 
 * Compilation: gcc -O2 -Wall -o perfect_tree perfect_binary_tree.c -lm
 * Usage: ./perfect_tree <depth>
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <sys/resource.h>
#include <unistd.h>

#define MAX_SAFE_DEPTH 30  // Beyond this, memory requirements exceed typical systems

/* Tree node structure using minimal memory footprint */
typedef struct TreeNode {
    int value;
    struct TreeNode *left;
    struct TreeNode *right;
} TreeNode;

/* Queue node for iterative BFS construction */
typedef struct QueueNode {
    TreeNode *tree_node;
    int depth;
    struct QueueNode *next;
} QueueNode;

/* Simple queue implementation for BFS */
typedef struct Queue {
    QueueNode *front;
    QueueNode *rear;
    size_t size;
} Queue;

/* Statistics structure */
typedef struct TreeStats {
    uint64_t total_nodes;
    size_t estimated_bytes;
    double estimated_mb;
    double build_time_sec;
    size_t actual_memory_kb;
} TreeStats;

/* Function prototypes */
TreeNode* create_node(int value);
Queue* create_queue(void);
void enqueue(Queue *q, TreeNode *node, int depth);
int dequeue(Queue *q, TreeNode **node, int *depth);
void free_queue(Queue *q);
TreeNode* build_tree_iterative(int depth, TreeStats *stats);
TreeNode* build_tree_recursive(int depth, int current_depth, int *counter);
void free_tree(TreeNode *root);
int verify_perfect_tree(TreeNode *root, int expected_depth);
uint64_t count_nodes(TreeNode *root);
void print_inorder(TreeNode *root);
size_t get_memory_usage_kb(void);
void calculate_memory_requirements(int depth, TreeStats *stats);

/* Create a new tree node with explicit malloc */
TreeNode* create_node(int value) {
    TreeNode *node = (TreeNode*)malloc(sizeof(TreeNode));
    if (node == NULL) {
        fprintf(stderr, "Error: malloc failed - out of memory\n");
        exit(EXIT_FAILURE);
    }
    
    node->value = value;
    node->left = NULL;
    node->right = NULL;
    
    return node;
}

/* Create queue for BFS */
Queue* create_queue(void) {
    Queue *q = (Queue*)malloc(sizeof(Queue));
    if (q == NULL) {
        fprintf(stderr, "Error: malloc failed for queue\n");
        exit(EXIT_FAILURE);
    }
    
    q->front = NULL;
    q->rear = NULL;
    q->size = 0;
    
    return q;
}

/* Enqueue operation */
void enqueue(Queue *q, TreeNode *node, int depth) {
    QueueNode *qnode = (QueueNode*)malloc(sizeof(QueueNode));
    if (qnode == NULL) {
        fprintf(stderr, "Error: malloc failed for queue node\n");
        exit(EXIT_FAILURE);
    }
    
    qnode->tree_node = node;
    qnode->depth = depth;
    qnode->next = NULL;
    
    if (q->rear == NULL) {
        q->front = q->rear = qnode;
    } else {
        q->rear->next = qnode;
        q->rear = qnode;
    }
    
    q->size++;
}

/* Dequeue operation */
int dequeue(Queue *q, TreeNode **node, int *depth) {
    if (q->front == NULL) {
        return 0;  // Queue is empty
    }
    
    QueueNode *temp = q->front;
    *node = temp->tree_node;
    *depth = temp->depth;
    
    q->front = q->front->next;
    
    if (q->front == NULL) {
        q->rear = NULL;
    }
    
    free(temp);
    q->size--;
    
    return 1;  // Success
}

/* Free queue memory */
void free_queue(Queue *q) {
    while (q->front != NULL) {
        QueueNode *temp = q->front;
        q->front = q->front->next;
        free(temp);
    }
    free(q);
}

/* Calculate memory requirements before allocation */
void calculate_memory_requirements(int depth, TreeStats *stats) {
    if (depth < 0) {
        stats->total_nodes = 0;
        stats->estimated_bytes = 0;
        stats->estimated_mb = 0.0;
        return;
    }
    
    // Calculate 2^(depth+1) - 1 safely
    if (depth > 62) {  // Prevent overflow
        fprintf(stderr, "Error: Depth too large (max 62)\n");
        exit(EXIT_FAILURE);
    }
    
    stats->total_nodes = (1ULL << (depth + 1)) - 1;
    stats->estimated_bytes = stats->total_nodes * sizeof(TreeNode);
    stats->estimated_mb = stats->estimated_bytes / (1024.0 * 1024.0);
}

/* Build perfect binary tree iteratively using BFS */
TreeNode* build_tree_iterative(int depth, TreeStats *stats) {
    if (depth < 0) {
        return NULL;
    }
    
    clock_t start = clock();
    
    TreeNode *root = create_node(0);
    int node_counter = 1;
    
    Queue *q = create_queue();
    enqueue(q, root, 0);
    
    TreeNode *current_node;
    int current_depth;
    
    while (dequeue(q, &current_node, &current_depth)) {
        if (current_depth < depth) {
            // Create left child
            current_node->left = create_node(node_counter++);
            enqueue(q, current_node->left, current_depth + 1);
            
            // Create right child
            current_node->right = create_node(node_counter++);
            enqueue(q, current_node->right, current_depth + 1);
        }
    }
    
    free_queue(q);
    
    clock_t end = clock();
    stats->build_time_sec = (double)(end - start) / CLOCKS_PER_SEC;
    
    return root;
}

/* Build perfect binary tree recursively (for shallow trees) */
TreeNode* build_tree_recursive(int depth, int current_depth, int *counter) {
    if (current_depth > depth) {
        return NULL;
    }
    
    TreeNode *node = create_node((*counter)++);
    
    if (current_depth < depth) {
        node->left = build_tree_recursive(depth, current_depth + 1, counter);
        node->right = build_tree_recursive(depth, current_depth + 1, counter);
    }
    
    return node;
}

/* Free entire tree using post-order traversal */
void free_tree(TreeNode *root) {
    if (root == NULL) {
        return;
    }
    
    free_tree(root->left);
    free_tree(root->right);
    free(root);
}

/* Verify that tree is perfect */
int verify_perfect_tree(TreeNode *root, int expected_depth) {
    if (root == NULL) {
        return expected_depth == -1;
    }
    
    // Helper function to get depth
    int get_depth(TreeNode *node) {
        if (node == NULL) {
            return -1;
        }
        
        int left_depth = get_depth(node->left);
        int right_depth = get_depth(node->right);
        
        // Check if perfect: left and right depths must be equal
        if (left_depth != right_depth) {
            return -999;  // Error marker
        }
        
        // Check if node has only one child
        if ((node->left == NULL) != (node->right == NULL)) {
            return -999;  // Error marker
        }
        
        return left_depth + 1;
    }
    
    int calculated_depth = get_depth(root);
    return calculated_depth == expected_depth;
}

/* Count total nodes in tree */
uint64_t count_nodes(TreeNode *root) {
    if (root == NULL) {
        return 0;
    }
    return 1 + count_nodes(root->left) + count_nodes(root->right);
}

/* Print in-order traversal (Left-Root-Right) */
void print_inorder(TreeNode *root) {
    if (root == NULL) {
        return;
    }
    
    print_inorder(root->left);
    printf("%d ", root->value);
    print_inorder(root->right);
}

/* Get current memory usage in KB using getrusage */
size_t get_memory_usage_kb(void) {
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    return (size_t)usage.ru_maxrss;  // In KB on Linux
}

/* Main function */
int main(int argc, char *argv[]) {
    int depth;
    TreeStats stats = {0};
    
    printf("======================================================================\n");
    printf("Perfect Binary Tree Construction in C with Explicit Memory Allocation\n");
    printf("======================================================================\n\n");
    
    // Parse command line argument
    if (argc > 1) {
        depth = atoi(argv[1]);
        if (depth < 0) {
            fprintf(stderr, "Error: Depth must be non-negative\n");
            return EXIT_FAILURE;
        }
        if (depth > MAX_SAFE_DEPTH) {
            fprintf(stderr, "Error: Depth %d exceeds safe limit %d\n", 
                    depth, MAX_SAFE_DEPTH);
            return EXIT_FAILURE;
        }
    } else {
        depth = 10;  // Default depth
    }
    
    printf("Requested tree depth: %d\n", depth);
    
    // Calculate memory requirements
    printf("\n--- Memory Analysis ---\n");
    calculate_memory_requirements(depth, &stats);
    
    printf("Total nodes to create: %lu\n", (unsigned long)stats.total_nodes);
    printf("Estimated memory: %.2f MB (%.4f GB)\n", 
           stats.estimated_mb, stats.estimated_mb / 1024.0);
    printf("Size per node: %lu bytes\n", sizeof(TreeNode));
    
    // Check available memory (simplified check)
    size_t initial_mem_kb = get_memory_usage_kb();
    printf("Initial memory usage: %.2f MB\n", initial_mem_kb / 1024.0);
    
    // Safety check for 8GB system
    if (stats.estimated_mb > 6000) {  // Leave 2GB for OS
        fprintf(stderr, "\n❌ ERROR: Memory requirement exceeds safe limit!\n");
        fprintf(stderr, "   Required: %.2f MB\n", stats.estimated_mb);
        fprintf(stderr, "   Safe limit: 6000 MB (leaving 2GB for system)\n");
        return EXIT_FAILURE;
    }
    
    printf("✓ Memory check passed\n");
    
    // Build the tree
    printf("\n--- Building Tree ---\n");
    
    TreeNode *root;
    if (depth <= 15) {
        printf("Using recursive build (suitable for shallow trees)...\n");
        int counter = 0;
        clock_t start = clock();
        root = build_tree_recursive(depth, 0, &counter);
        clock_t end = clock();
        stats.build_time_sec = (double)(end - start) / CLOCKS_PER_SEC;
    } else {
        printf("Using iterative build (suitable for deep trees)...\n");
        root = build_tree_iterative(depth, &stats);
    }
    
    size_t final_mem_kb = get_memory_usage_kb();
    stats.actual_memory_kb = final_mem_kb;
    
    printf("Build completed in %.6f seconds\n", stats.build_time_sec);
    printf("Final memory usage: %.2f MB\n", final_mem_kb / 1024.0);
    printf("Memory increase: %.2f MB\n", (final_mem_kb - initial_mem_kb) / 1024.0);
    
    // Verify tree structure
    printf("\n--- Verification ---\n");
    uint64_t node_count = count_nodes(root);
    int is_perfect = verify_perfect_tree(root, depth);
    
    printf("Nodes counted: %lu\n", (unsigned long)node_count);
    printf("Expected nodes: %lu\n", (unsigned long)stats.total_nodes);
    printf("Tree is perfect: %s\n", is_perfect ? "✓ Yes" : "✗ No");
    
    // Show small traversal sample
    if (depth <= 4) {
        printf("\n--- In-order Traversal ---\n");
        printf("Values: ");
        print_inorder(root);
        printf("\n");
    }
    
    // Keep tree in memory - demonstrate it's not freed yet
    printf("\n--- Memory Retention Test ---\n");
    printf("Tree is still in memory (not freed)\n");
    printf("Root node value: %d\n", root->value);
    printf("Root has left child: %s\n", root->left ? "Yes" : "No");
    printf("Root has right child: %s\n", root->right ? "Yes" : "No");
    
    // Explicitly free tree memory
    printf("\n--- Explicit Memory Deallocation ---\n");
    printf("Freeing all tree nodes...\n");
    
    free_tree(root);
    root = NULL;
    
    size_t after_free_mem_kb = get_memory_usage_kb();
    printf("Memory after free: %.2f MB\n", after_free_mem_kb / 1024.0);
    printf("Memory freed: %.2f MB\n", (final_mem_kb - after_free_mem_kb) / 1024.0);
    
    printf("\n======================================================================\n");
    printf("Execution completed successfully!\n");
    printf("======================================================================\n");
    
    return EXIT_SUCCESS;
}

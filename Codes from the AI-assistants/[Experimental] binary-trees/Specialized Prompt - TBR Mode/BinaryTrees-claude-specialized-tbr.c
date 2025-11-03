#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/sysinfo.h>
#include <unistd.h>

/* 
 * AVL Tree implementation using memory addresses as implicit values
 * No actual data storage - the allocation pattern itself IS the data
 */

#define MAX_MEMORY_USAGE (6UL * 1024 * 1024 * 1024) // 6GB safety limit
#define NODE_SIZE sizeof(AVLNode)

typedef struct AVLNode {
    struct AVLNode *left;
    struct AVLNode *right;
    struct AVLNode *parent;
    int height;
    // No data field - the address IS the value
} AVLNode;

typedef struct {
    AVLNode *root;
    size_t node_count;
    size_t memory_used;
} AVLTree;

// Function prototypes
static inline int max(int a, int b) { return (a > b) ? a : b; }
static inline int height(AVLNode *node) { return node ? node->height : 0; }
static inline int balance_factor(AVLNode *node) { 
    return node ? height(node->left) - height(node->right) : 0; 
}

// Memory management with system constraints
static int check_memory_available(AVLTree *tree) {
    struct sysinfo info;
    if (sysinfo(&info) != 0) return 0;
    
    unsigned long available = info.freeram * info.mem_unit;
    unsigned long current_usage = tree->memory_used;
    
    // Ensure we stay under 75% of RAM and under our defined limit
    return (current_usage + NODE_SIZE < MAX_MEMORY_USAGE) && 
           (current_usage + NODE_SIZE < available * 0.75);
}

static AVLNode* create_node(AVLTree *tree) {
    if (!check_memory_available(tree)) {
        fprintf(stderr, "Memory limit reached\n");
        return NULL;
    }
    
    AVLNode *node = (AVLNode*)malloc(sizeof(AVLNode));
    if (!node) return NULL;
    
    node->left = NULL;
    node->right = NULL;
    node->parent = NULL;
    node->height = 1;
    
    tree->memory_used += NODE_SIZE;
    tree->node_count++;
    
    return node;
}

static void update_height(AVLNode *node) {
    if (node) {
        node->height = 1 + max(height(node->left), height(node->right));
    }
}

// AVL Rotations for perfect balance
static AVLNode* rotate_right(AVLNode *y) {
    AVLNode *x = y->left;
    AVLNode *T2 = x->right;
    
    x->right = y;
    y->left = T2;
    
    x->parent = y->parent;
    y->parent = x;
    if (T2) T2->parent = y;
    
    update_height(y);
    update_height(x);
    
    return x;
}

static AVLNode* rotate_left(AVLNode *x) {
    AVLNode *y = x->right;
    AVLNode *T2 = y->left;
    
    y->left = x;
    x->right = T2;
    
    y->parent = x->parent;
    x->parent = y;
    if (T2) T2->parent = x;
    
    update_height(x);
    update_height(y);
    
    return y;
}

// Compare nodes by their memory addresses (implicit values)
static inline int compare_nodes(AVLNode *a, AVLNode *b) {
    uintptr_t addr_a = (uintptr_t)a;
    uintptr_t addr_b = (uintptr_t)b;
    
    if (addr_a < addr_b) return -1;
    if (addr_a > addr_b) return 1;
    return 0;
}

// Insert and rebalance
static AVLNode* insert_recursive(AVLNode *node, AVLNode *new_node) {
    if (!node) return new_node;
    
    int cmp = compare_nodes(new_node, node);
    
    if (cmp < 0) {
        node->left = insert_recursive(node->left, new_node);
        if (node->left) node->left->parent = node;
    } else if (cmp > 0) {
        node->right = insert_recursive(node->right, new_node);
        if (node->right) node->right->parent = node;
    } else {
        return node; // Duplicate (shouldn't happen with unique addresses)
    }
    
    update_height(node);
    
    int balance = balance_factor(node);
    
    // Left-Left Case
    if (balance > 1 && compare_nodes(new_node, node->left) < 0)
        return rotate_right(node);
    
    // Right-Right Case
    if (balance < -1 && compare_nodes(new_node, node->right) > 0)
        return rotate_left(node);
    
    // Left-Right Case
    if (balance > 1 && compare_nodes(new_node, node->left) > 0) {
        node->left = rotate_left(node->left);
        return rotate_right(node);
    }
    
    // Right-Left Case
    if (balance < -1 && compare_nodes(new_node, node->right) < 0) {
        node->right = rotate_right(node->right);
        return rotate_left(node);
    }
    
    return node;
}

// Public insertion interface
int avl_insert(AVLTree *tree) {
    AVLNode *new_node = create_node(tree);
    if (!new_node) return 0;
    
    tree->root = insert_recursive(tree->root, new_node);
    if (tree->root) tree->root->parent = NULL;
    
    return 1;
}

// Tree traversals
void inorder_traversal(AVLNode *node, void (*visit)(AVLNode*)) {
    if (!node) return;
    inorder_traversal(node->left, visit);
    visit(node);
    inorder_traversal(node->right, visit);
}

void preorder_traversal(AVLNode *node, void (*visit)(AVLNode*)) {
    if (!node) return;
    visit(node);
    preorder_traversal(node->left, visit);
    preorder_traversal(node->right, visit);
}

void postorder_traversal(AVLNode *node, void (*visit)(AVLNode*)) {
    if (!node) return;
    postorder_traversal(node->left, visit);
    postorder_traversal(node->right, visit);
    visit(node);
}

// Verification and statistics
int verify_balance(AVLNode *node, int *is_balanced) {
    if (!node) return 0;
    
    int left_height = verify_balance(node->left, is_balanced);
    int right_height = verify_balance(node->right, is_balanced);
    
    if (abs(left_height - right_height) > 1) {
        *is_balanced = 0;
    }
    
    return 1 + max(left_height, right_height);
}

void print_tree_stats(AVLTree *tree) {
    printf("\n=== Tree Statistics ===\n");
    printf("Total nodes: %zu\n", tree->node_count);
    printf("Memory used: %.2f MB\n", tree->memory_used / (1024.0 * 1024.0));
    printf("Tree height: %d\n", height(tree->root));
    
    int balanced = 1;
    verify_balance(tree->root, &balanced);
    printf("Perfectly balanced: %s\n", balanced ? "YES" : "NO");
    
    if (tree->root) {
        printf("Root address: %p\n", (void*)tree->root);
    }
}

// Cleanup
void destroy_tree(AVLNode *node) {
    if (!node) return;
    destroy_tree(node->left);
    destroy_tree(node->right);
    free(node);
}

void avl_destroy(AVLTree *tree) {
    destroy_tree(tree->root);
    tree->root = NULL;
    tree->node_count = 0;
    tree->memory_used = 0;
}

// Initialize tree
void avl_init(AVLTree *tree) {
    tree->root = NULL;
    tree->node_count = 0;
    tree->memory_used = 0;
}

// Visitor function for display
static void print_node(AVLNode *node) {
    printf("Node@%p (h=%d, bf=%d)\n", 
           (void*)node, node->height, balance_factor(node));
}

// Demo program
int main(void) {
    AVLTree tree;
    avl_init(&tree);
    
    printf("Building perfectly balanced AVL tree using memory addresses...\n");
    printf("System: Ubuntu 24.04.4 64-bit\n");
    printf("Memory safety limit: %.2f GB\n\n", MAX_MEMORY_USAGE / (1024.0*1024.0*1024.0));
    
    // Insert nodes - each allocation creates a unique address
    const int NUM_NODES = 1000;
    
    for (int i = 0; i < NUM_NODES; i++) {
        if (!avl_insert(&tree)) {
            fprintf(stderr, "Failed to insert node %d\n", i);
            break;
        }
        
        if ((i + 1) % 100 == 0) {
            printf("Inserted %d nodes...\n", i + 1);
        }
    }
    
    print_tree_stats(&tree);
    
    printf("\n=== First 10 nodes (in-order traversal) ===\n");
    int count = 0;
    void print_limited(AVLNode *node) {
        if (count++ < 10) print_node(node);
    }
    inorder_traversal(tree.root, print_limited);
    
    // Cleanup
    printf("\nCleaning up...\n");
    avl_destroy(&tree);
    printf("Done!\n");
    
    return 0;
}
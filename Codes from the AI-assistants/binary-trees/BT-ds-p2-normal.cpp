#include <iostream>
#include <vector>
#include <memory>
#include <cmath>
#include <chrono>
#include <sys/resource.h>
#include <unistd.h>
#include <iomanip>

class TreeNode {
public:
    int data;
    TreeNode* left;
    TreeNode* right;
    
    TreeNode(int val) : data(val), left(nullptr), right(nullptr) {}
};

class MemoryManager {
private:
    std::vector<TreeNode*> allocated_nodes;
    size_t total_memory_used;
    
public:
    MemoryManager() : total_memory_used(0) {}
    
    TreeNode* allocate_node(int val) {
        TreeNode* node = new TreeNode(val);
        allocated_nodes.push_back(node);
        total_memory_used += sizeof(TreeNode);
        return node;
    }
    
    size_t get_total_memory() const {
        return total_memory_used;
    }
    
    size_t get_node_count() const {
        return allocated_nodes.size();
    }
    
    void deallocate_all() {
        for (TreeNode* node : allocated_nodes) {
            delete node;
        }
        allocated_nodes.clear();
        total_memory_used = 0;
    }
    
    ~MemoryManager() {
        deallocate_all();
    }
};

class PerfectBinaryTree {
private:
    TreeNode* root;
    MemoryManager& mem_manager;
    
    // Pre-order construction for perfect binary tree
    TreeNode* build_tree_preorder(int depth, int current_depth, int& counter) {
        if (current_depth > depth) {
            return nullptr;
        }
        
        TreeNode* node = mem_manager.allocate_node(counter++);
        
        // For perfect binary tree, build both subtrees if not at max depth
        if (current_depth < depth) {
            node->left = build_tree_preorder(depth, current_depth + 1, counter);
            node->right = build_tree_preorder(depth, current_depth + 1, counter);
        }
        
        return node;
    }
    
    // Iterative construction using BFS (more memory efficient for deep trees)
    TreeNode* build_tree_iterative(int depth) {
        if (depth < 0) return nullptr;
        
        int counter = 1;
        root = mem_manager.allocate_node(counter++);
        
        // Using vector as a queue for level-order construction
        std::vector<TreeNode*> current_level;
        current_level.push_back(root);
        
        for (int d = 0; d < depth - 1; d++) {
            std::vector<TreeNode*> next_level;
            
            for (TreeNode* parent : current_level) {
                parent->left = mem_manager.allocate_node(counter++);
                parent->right = mem_manager.allocate_node(counter++);
                
                next_level.push_back(parent->left);
                next_level.push_back(parent->right);
            }
            
            current_level = std::move(next_level);
        }
        
        return root;
    }
    
    // Memory-efficient construction using array representation
    std::vector<TreeNode*> build_tree_array_representation(int depth) {
        int total_nodes = (1 << depth) - 1; // 2^depth - 1
        std::vector<TreeNode*> tree_array(total_nodes, nullptr);
        
        for (int i = 0; i < total_nodes; i++) {
            tree_array[i] = mem_manager.allocate_node(i + 1);
        }
        
        // Set up parent-child relationships
        for (int i = 0; i < total_nodes; i++) {
            int left_child = 2 * i + 1;
            int right_child = 2 * i + 2;
            
            if (left_child < total_nodes) {
                tree_array[i]->left = tree_array[left_child];
            }
            if (right_child < total_nodes) {
                tree_array[i]->right = tree_array[right_child];
            }
        }
        
        if (total_nodes > 0) {
            root = tree_array[0];
        }
        
        return tree_array;
    }
    
    void print_tree(TreeNode* node, int depth, int max_depth) {
        if (!node || depth > max_depth) return;
        
        std::cout << std::string(depth * 2, ' ') << node->data << "\n";
        
        if (node->left) {
            print_tree(node->left, depth + 1, max_depth);
        }
        if (node->right) {
            print_tree(node->right, depth + 1, max_depth);
        }
    }
    
public:
    PerfectBinaryTree(MemoryManager& manager) : root(nullptr), mem_manager(manager) {}
    
    // Method 1: Recursive construction (uses call stack memory)
    void build_recursive(int depth) {
        if (depth < 0) {
            std::cerr << "Depth must be non-negative\n";
            return;
        }
        
        int counter = 1;
        root = build_tree_preorder(depth, 0, counter);
    }
    
    // Method 2: Iterative construction (BFS, avoids deep recursion)
    void build_iterative(int depth) {
        if (depth < 0) {
            std::cerr << "Depth must be non-negative\n";
            return;
        }
        
        root = build_tree_iterative(depth);
    }
    
    // Method 3: Array-based construction (most memory efficient)
    void build_using_array(int depth) {
        if (depth < 0) {
            std::cerr << "Depth must be non-negative\n";
            return;
        }
        
        build_tree_array_representation(depth);
    }
    
    TreeNode* get_root() const {
        return root;
    }
    
    void display(int max_display_depth = 3) {
        if (!root) {
            std::cout << "Tree is empty\n";
            return;
        }
        
        std::cout << "Tree structure (showing first " << max_display_depth << " levels):\n";
        print_tree(root, 0, max_display_depth);
    }
    
    // Calculate theoretical memory usage
    static size_t calculate_theoretical_memory(int depth) {
        size_t node_count = (depth >= 0) ? ((1ULL << depth) - 1) : 0;
        return node_count * sizeof(TreeNode);
    }
};

// Memory monitoring utility
class SystemMonitor {
public:
    static void print_memory_info() {
        struct rusage usage;
        getrusage(RUSAGE_SELF, &usage);
        
        std::cout << "\n=== Memory Usage ===" << std::endl;
        std::cout << "Max RSS: " << usage.ru_maxrss / 1024 << " MB" << std::endl;
        
        // Read from /proc/self/status for more detailed info
        FILE* status = fopen("/proc/self/status", "r");
        if (status) {
            char line[128];
            while (fgets(line, sizeof(line), status)) {
                if (strncmp(line, "VmSize:", 7) == 0 ||
                    strncmp(line, "VmRSS:", 6) == 0 ||
                    strncmp(line, "VmPeak:", 7) == 0) {
                    std::cout << line;
                }
            }
            fclose(status);
        }
    }
    
    static size_t get_available_memory() {
        long pages = sysconf(_SC_AVPHYS_PAGES);
        long page_size = sysconf(_SC_PAGE_SIZE);
        return pages * page_size;
    }
};

// Safety check function
bool check_system_limits(int depth) {
    size_t node_count = (1ULL << depth) - 1;
    size_t required_memory = node_count * sizeof(TreeNode);
    size_t available_memory = SystemMonitor::get_available_memory();
    
    std::cout << "\n=== System Check ===" << std::endl;
    std::cout << "Requested depth: " << depth << std::endl;
    std::cout << "Total nodes: " << node_count << std::endl;
    std::cout << "Estimated memory required: " 
              << std::fixed << std::setprecision(2)
              << required_memory / (1024.0 * 1024.0) << " MB" << std::endl;
    std::cout << "Available memory: " 
              << available_memory / (1024.0 * 1024.0) << " MB" << std::endl;
    
    // Safety threshold: don't use more than 70% of available memory
    if (required_memory > available_memory * 0.7) {
        std::cerr << "WARNING: Requested tree depth may exceed safe memory limits!" << std::endl;
        std::cerr << "Consider reducing depth or using a different construction method." << std::endl;
        return false;
    }
    
    return true;
}

int main() {
    std::cout << "=== Perfect Binary Tree Constructor ===" << std::endl;
    std::cout << "System: Ubuntu 24.04.4 64-bit" << std::endl;
    std::cout << "RAM: 8 GB, SSD: 256 GB" << std::endl;
    
    int depth;
    std::cout << "\nEnter tree depth (N): ";
    std::cin >> depth;
    
    if (depth < 0 || depth > 25) { // Practical limit for 8GB RAM
        std::cerr << "Depth must be between 0 and 25 for this system configuration." << std::endl;
        return 1;
    }
    
    if (!check_system_limits(depth)) {
        std::cout << "Proceed anyway? (y/n): ";
        char choice;
        std::cin >> choice;
        if (choice != 'y' && choice != 'Y') {
            return 0;
        }
    }
    
    // Choose construction method
    int method;
    std::cout << "\nSelect construction method:" << std::endl;
    std::cout << "1. Recursive (for depth <= 15)" << std::endl;
    std::cout << "2. Iterative BFS (for depth <= 20)" << std::endl;
    std::cout << "3. Array-based (most efficient, for depth <= 25)" << std::endl;
    std::cout << "Choice: ";
    std::cin >> method;
    
    // Create memory manager
    MemoryManager mem_manager;
    
    // Create and build tree
    PerfectBinaryTree tree(mem_manager);
    
    auto start = std::chrono::high_resolution_clock::now();
    
    try {
        switch (method) {
            case 1:
                tree.build_recursive(depth);
                break;
            case 2:
                tree.build_iterative(depth);
                break;
            case 3:
                tree.build_using_array(depth);
                break;
            default:
                std::cerr << "Invalid method choice. Using array-based method." << std::endl;
                tree.build_using_array(depth);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        // Display results
        std::cout << "\n=== Construction Complete ===" << std::endl;
        std::cout << "Construction time: " << duration.count() << " ms" << std::endl;
        std::cout << "Total nodes allocated: " << mem_manager.get_node_count() << std::endl;
        std::cout << "Memory used by tree nodes: " 
                  << mem_manager.get_total_memory() / (1024.0 * 1024.0) << " MB" << std::endl;
        
        // Display tree structure (first few levels)
        if (depth <= 5) {
            tree.display(depth);
        } else {
            tree.display(3);
        }
        
        // Keep tree in memory before GC
        std::cout << "\nTree is now in memory. Press Enter to trigger garbage collection...";
        std::cin.ignore();
        std::cin.get();
        
        // Manual garbage collection
        std::cout << "\nDeallocating tree..." << std::endl;
        mem_manager.deallocate_all();
        std::cout << "All nodes deallocated." << std::endl;
        
    } catch (const std::bad_alloc& e) {
        std::cerr << "\nERROR: Memory allocation failed! " << e.what() << std::endl;
        std::cerr << "System ran out of memory." << std::endl;
        return 1;
    }
    
    SystemMonitor::print_memory_info();
    
    return 0;
}
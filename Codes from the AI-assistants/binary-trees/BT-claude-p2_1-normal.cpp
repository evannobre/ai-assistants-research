/**
 * Perfect Binary Tree Construction with Manual Memory Allocation
 * 
 * Author: Computer Scientist specialized in back-end development
 * Target: Ubuntu 24.04.4 64-bit, 8GB RAM, 256GB SSD
 * 
 * Compilation:
 *   g++ -std=c++17 -O3 -o perfect_tree perfect_binary_tree.cpp
 * 
 * Features:
 * - Custom memory allocator with arena allocation
 * - Memory pool for efficient node allocation
 * - RAII principles for automatic cleanup
 * - Cache-friendly memory layout
 * - Detailed memory tracking and statistics
 */

#include <iostream>
#include <memory>
#include <chrono>
#include <cmath>
#include <cstring>
#include <queue>
#include <vector>
#include <iomanip>
#include <stdexcept>
#include <sys/resource.h>
#include <unistd.h>

// Constants
constexpr size_t BYTES_PER_MB = 1024 * 1024;
constexpr size_t AVAILABLE_RAM_GB = 8;
constexpr size_t SAFETY_MARGIN_MB = 2048; // Reserve 2GB for OS

/**
 * TreeNode structure with minimal memory footprint
 * Size: 24 bytes (8 bytes value + 8 bytes left + 8 bytes right)
 */
struct TreeNode {
    int64_t value;
    TreeNode* left;
    TreeNode* right;
    
    TreeNode(int64_t val) : value(val), left(nullptr), right(nullptr) {}
};

/**
 * Memory statistics tracker
 */
struct MemoryStats {
    size_t nodes_created = 0;
    size_t total_bytes_allocated = 0;
    size_t peak_bytes_allocated = 0;
    double construction_time_sec = 0.0;
    int tree_depth = 0;
    
    void print() const {
        std::cout << "\n" << std::string(60, '=') << "\n";
        std::cout << "Memory Statistics\n";
        std::cout << std::string(60, '=') << "\n";
        std::cout << "Nodes created:       " << nodes_created << "\n";
        std::cout << "Total allocated:     " << (total_bytes_allocated / BYTES_PER_MB) 
                  << " MB\n";
        std::cout << "Peak allocated:      " << (peak_bytes_allocated / BYTES_PER_MB) 
                  << " MB\n";
        std::cout << "Construction time:   " << std::fixed << std::setprecision(3) 
                  << construction_time_sec << " seconds\n";
        std::cout << "Nodes per second:    " 
                  << static_cast<size_t>(nodes_created / construction_time_sec) << "\n";
        std::cout << "Bytes per node:      " 
                  << (nodes_created > 0 ? total_bytes_allocated / nodes_created : 0) << "\n";
        std::cout << std::string(60, '=') << "\n\n";
    }
};

/**
 * Arena Allocator for efficient bulk allocation
 * 
 * Benefits:
 * - Reduces malloc/free overhead
 * - Improves cache locality
 * - Enables batch deallocation
 * - Reduces memory fragmentation
 */
class ArenaAllocator {
private:
    static constexpr size_t ARENA_SIZE = 64 * BYTES_PER_MB; // 64 MB chunks
    
    struct Arena {
        char* buffer;
        size_t size;
        size_t used;
        Arena* next;
        
        Arena(size_t sz) : size(sz), used(0), next(nullptr) {
            buffer = new char[size];
        }
        
        ~Arena() {
            delete[] buffer;
        }
    };
    
    Arena* current_arena;
    Arena* first_arena;
    size_t total_allocated;
    
public:
    ArenaAllocator() : current_arena(nullptr), first_arena(nullptr), total_allocated(0) {
        allocate_new_arena(ARENA_SIZE);
    }
    
    ~ArenaAllocator() {
        Arena* arena = first_arena;
        while (arena) {
            Arena* next = arena->next;
            delete arena;
            arena = next;
        }
    }
    
    void* allocate(size_t size) {
        // Align to 8 bytes for better performance
        size = (size + 7) & ~7;
        
        // Check if current arena has enough space
        if (current_arena->used + size > current_arena->size) {
            allocate_new_arena(std::max(ARENA_SIZE, size * 2));
        }
        
        void* ptr = current_arena->buffer + current_arena->used;
        current_arena->used += size;
        total_allocated += size;
        
        return ptr;
    }
    
    size_t get_total_allocated() const {
        return total_allocated;
    }
    
private:
    void allocate_new_arena(size_t size) {
        Arena* new_arena = new Arena(size);
        
        if (first_arena == nullptr) {
            first_arena = new_arena;
            current_arena = new_arena;
        } else {
            current_arena->next = new_arena;
            current_arena = new_arena;
        }
    }
};

/**
 * Perfect Binary Tree Builder
 */
class PerfectBinaryTreeBuilder {
private:
    TreeNode* root;
    ArenaAllocator allocator;
    MemoryStats stats;
    
public:
    PerfectBinaryTreeBuilder() : root(nullptr) {}
    
    /**
     * Calculate theoretical memory requirement
     */
    size_t estimate_memory_requirement(int depth) const {
        if (depth < 0) return 0;
        
        // Total nodes = 2^(depth+1) - 1
        size_t total_nodes = (1ULL << (depth + 1)) - 1;
        size_t bytes_per_node = sizeof(TreeNode);
        size_t total_bytes = total_nodes * bytes_per_node;
        
        return total_bytes;
    }
    
    /**
     * Check if construction is feasible
     */
    bool check_memory_feasibility(int depth) const {
        size_t required_bytes = estimate_memory_requirement(depth);
        size_t required_mb = required_bytes / BYTES_PER_MB;
        
        // Get available memory from system
        size_t available_mb = get_available_memory_mb();
        
        std::cout << "\n" << std::string(60, '=') << "\n";
        std::cout << "Memory Feasibility Analysis for Depth " << depth << "\n";
        std::cout << std::string(60, '=') << "\n";
        std::cout << "Total nodes required: " << ((1ULL << (depth + 1)) - 1) << "\n";
        std::cout << "Estimated memory:     " << required_mb << " MB\n";
        std::cout << "Available memory:     " << available_mb << " MB\n";
        std::cout << "Safety margin:        " << SAFETY_MARGIN_MB << " MB\n";
        std::cout << "Feasible:             " 
                  << (required_mb + SAFETY_MARGIN_MB <= available_mb ? "YES" : "NO") 
                  << "\n";
        std::cout << std::string(60, '=') << "\n\n";
        
        return required_mb + SAFETY_MARGIN_MB <= available_mb;
    }
    
    /**
     * Build perfect binary tree using iterative approach
     * 
     * Algorithm: Level-order (BFS) construction
     * - Better cache locality
     * - Predictable memory access pattern
     * - No stack overflow risk
     */
    bool build_iterative(int depth) {
        if (depth < 0) {
            std::cerr << "Error: Depth must be non-negative\n";
            return false;
        }
        
        if (depth > 35) {
            std::cerr << "Error: Depth > 35 would require excessive memory\n";
            return false;
        }
        
        if (!check_memory_feasibility(depth)) {
            std::cerr << "Error: Insufficient memory for requested depth\n";
            return false;
        }
        
        auto start_time = std::chrono::high_resolution_clock::now();
        
        std::cout << "Building perfect binary tree of depth " << depth 
                  << " using iterative method...\n";
        
        try {
            // Create root
            root = new (allocator.allocate(sizeof(TreeNode))) TreeNode(1);
            stats.nodes_created++;
            
            if (depth == 0) {
                update_final_stats(start_time, depth);
                return true;
            }
            
            // Queue for level-order construction
            std::queue<std::pair<TreeNode*, int>> queue;
            queue.push({root, 0});
            
            size_t progress_interval = 1000000; // Report every 1M nodes
            
            while (!queue.empty()) {
                auto [node, current_depth] = queue.front();
                queue.pop();
                
                if (current_depth < depth) {
                    int64_t left_value = node->value * 2;
                    int64_t right_value = node->value * 2 + 1;
                    
                    // Allocate left child
                    node->left = new (allocator.allocate(sizeof(TreeNode))) 
                                 TreeNode(left_value);
                    stats.nodes_created++;
                    queue.push({node->left, current_depth + 1});
                    
                    // Allocate right child
                    node->right = new (allocator.allocate(sizeof(TreeNode))) 
                                  TreeNode(right_value);
                    stats.nodes_created++;
                    queue.push({node->right, current_depth + 1});
                    
                    // Progress reporting
                    if (stats.nodes_created % progress_interval == 0) {
                        size_t current_mb = allocator.get_total_allocated() / BYTES_PER_MB;
                        std::cout << "Progress: " << stats.nodes_created 
                                  << " nodes created, Memory: " << current_mb 
                                  << " MB, Queue size: " << queue.size() << "\n";
                    }
                }
            }
            
            update_final_stats(start_time, depth);
            return true;
            
        } catch (const std::bad_alloc& e) {
            std::cerr << "Error: Out of memory during tree construction\n";
            return false;
        }
    }
    
    /**
     * Build perfect binary tree using recursive approach
     */
    TreeNode* build_recursive_helper(int depth, int current_depth, int64_t value) {
        if (current_depth > depth) {
            return nullptr;
        }
        
        // Allocate node from arena
        TreeNode* node = new (allocator.allocate(sizeof(TreeNode))) TreeNode(value);
        stats.nodes_created++;
        
        // Progress reporting
        if (stats.nodes_created % 1000000 == 0) {
            size_t current_mb = allocator.get_total_allocated() / BYTES_PER_MB;
            std::cout << "Progress: " << stats.nodes_created 
                      << " nodes created, Memory: " << current_mb << " MB\n";
        }
        
        // Recursively build children
        if (current_depth < depth) {
            node->left = build_recursive_helper(depth, current_depth + 1, value * 2);
            node->right = build_recursive_helper(depth, current_depth + 1, value * 2 + 1);
        }
        
        return node;
    }
    
    bool build_recursive(int depth) {
        if (depth < 0) {
            std::cerr << "Error: Depth must be non-negative\n";
            return false;
        }
        
        // Recursive approach limited by stack size
        if (depth > 25) {
            std::cerr << "Error: Depth > 25 may cause stack overflow (use iterative)\n";
            return false;
        }
        
        if (!check_memory_feasibility(depth)) {
            std::cerr << "Error: Insufficient memory for requested depth\n";
            return false;
        }
        
        auto start_time = std::chrono::high_resolution_clock::now();
        
        std::cout << "Building perfect binary tree of depth " << depth 
                  << " using recursive method...\n";
        
        try {
            root = build_recursive_helper(depth, 0, 1);
            update_final_stats(start_time, depth);
            return true;
            
        } catch (const std::bad_alloc& e) {
            std::cerr << "Error: Out of memory during tree construction\n";
            return false;
        }
    }
    
    /**
     * Verify tree structure
     */
    bool verify_tree() const {
        if (!root) return false;
        
        auto get_depth = [](TreeNode* node, auto& get_depth_ref) -> int {
            if (!node) return -1;
            return 1 + std::max(get_depth_ref(node->left, get_depth_ref),
                               get_depth_ref(node->right, get_depth_ref));
        };
        
        auto is_perfect = [](TreeNode* node, int depth, int level, 
                            auto& is_perfect_ref) -> bool {
            if (!node) return true;
            
            if (!node->left && !node->right) {
                return level == depth;
            }
            
            if (!node->left || !node->right) {
                return false;
            }
            
            return is_perfect_ref(node->left, depth, level + 1, is_perfect_ref) &&
                   is_perfect_ref(node->right, depth, level + 1, is_perfect_ref);
        };
        
        int depth = get_depth(root, get_depth);
        bool valid = is_perfect(root, depth, 0, is_perfect);
        
        std::cout << "Tree verification: " << (valid ? "PASSED" : "FAILED") << "\n";
        std::cout << "Tree depth: " << depth << "\n\n";
        
        return valid;
    }
    
    /**
     * Get memory statistics
     */
    const MemoryStats& get_stats() const {
        return stats;
    }
    
    /**
     * Print tree information
     */
    void print_info() const {
        stats.print();
    }
    
private:
    void update_final_stats(const std::chrono::high_resolution_clock::time_point& start_time,
                           int depth) {
        auto end_time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = end_time - start_time;
        
        stats.construction_time_sec = elapsed.count();
        stats.total_bytes_allocated = allocator.get_total_allocated();
        stats.peak_bytes_allocated = stats.total_bytes_allocated;
        stats.tree_depth = depth;
        
        std::cout << "\n" << std::string(60, '=') << "\n";
        std::cout << "Construction Complete!\n";
        std::cout << std::string(60, '=') << "\n";
        std::cout << "Nodes created:       " << stats.nodes_created << "\n";
        std::cout << "Expected nodes:      " << ((1ULL << (depth + 1)) - 1) << "\n";
        std::cout << "Construction time:   " << std::fixed << std::setprecision(3) 
                  << stats.construction_time_sec << " seconds\n";
        std::cout << "Memory used:         " 
                  << (stats.total_bytes_allocated / BYTES_PER_MB) << " MB\n";
        std::cout << "Nodes per second:    " 
                  << static_cast<size_t>(stats.nodes_created / stats.construction_time_sec) 
                  << "\n";
        std::cout << std::string(60, '=') << "\n\n";
    }
    
    size_t get_available_memory_mb() const {
        // Get available memory from /proc/meminfo
        size_t available_kb = 0;
        FILE* fp = fopen("/proc/meminfo", "r");
        if (fp) {
            char line[256];
            while (fgets(line, sizeof(line), fp)) {
                if (sscanf(line, "MemAvailable: %zu kB", &available_kb) == 1) {
                    break;
                }
            }
            fclose(fp);
        }
        
        return available_kb / 1024; // Convert to MB
    }
};

/**
 * Main function
 */
int main(int argc, char* argv[]) {
    std::cout << "Perfect Binary Tree Builder (C++)\n";
    std::cout << std::string(60, '=') << "\n";
    std::cout << "System Information:\n";
    std::cout << "sizeof(TreeNode):    " << sizeof(TreeNode) << " bytes\n";
    std::cout << "sizeof(TreeNode*):   " << sizeof(TreeNode*) << " bytes\n";
    
    // Get system page size
    long page_size = sysconf(_SC_PAGESIZE);
    std::cout << "Page size:           " << page_size << " bytes\n";
    
    std::cout << std::string(60, '=') << "\n\n";
    
    // Default depth (can be changed)
    int depth = 20; // ~2M nodes, ~48 MB
    
    if (argc > 1) {
        depth = std::atoi(argv[1]);
    }
    
    // Recommended depths for 8GB RAM:
    // Depth 20: ~2M nodes, ~48 MB
    // Depth 22: ~8M nodes, ~201 MB
    // Depth 24: ~33M nodes, ~805 MB
    // Depth 26: ~134M nodes, ~3.2 GB
    // Depth 27: ~268M nodes, ~6.4 GB
    
    PerfectBinaryTreeBuilder builder;
    
    // Build using iterative method (recommended)
    bool success = builder.build_iterative(depth);
    
    if (success) {
        // Verify tree structure
        builder.verify_tree();
        
        // Print detailed statistics
        builder.print_info();
        
        std::cout << "[Tree is now built and in memory]\n";
        std::cout << "[All nodes remain allocated until program terminates]\n";
        std::cout << "[No garbage collection - manual memory management]\n\n";
        
        // Tree remains in memory and can be used for operations
        // The ArenaAllocator's destructor will clean up all memory
        // when the builder goes out of scope
    } else {
        std::cerr << "Failed to build tree\n";
        return 1;
    }
    
    return 0;
}

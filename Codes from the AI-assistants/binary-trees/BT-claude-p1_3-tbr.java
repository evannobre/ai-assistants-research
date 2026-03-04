/*
 * Perfect Binary Tree Memory Allocator in Java
 * Demonstrates heap allocation with GC control and memory tracking
 * Uses native Java memory management and Runtime API
 */

import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.MemoryUsage;

/**
 * Binary tree node class
 */
class TreeNode {
    int value;
    TreeNode left;
    TreeNode right;
    
    public TreeNode(int value) {
        this.value = value;
        this.left = null;
        this.right = null;
    }
}

/**
 * Statistics tracker for memory allocation
 */
class AllocationStats {
    long nodeCount = 0;
    long startTime = 0;
    long endTime = 0;
    long memoryBefore = 0;
    long memoryAfter = 0;
    
    public void reset() {
        nodeCount = 0;
        startTime = 0;
        endTime = 0;
        memoryBefore = 0;
        memoryAfter = 0;
    }
    
    public void printStats(int depth) {
        long expectedNodes = (1L << (depth + 1)) - 1;
        double timeTaken = (endTime - startTime) / 1000.0;
        long memoryUsed = memoryAfter - memoryBefore;
        
        System.out.println();
        System.out.println("============================================================");
        System.out.println("Memory Allocation Statistics");
        System.out.println("============================================================");
        System.out.printf("  Target depth:           %d%n", depth);
        System.out.printf("  Expected nodes:         %,d%n", expectedNodes);
        System.out.printf("  Actual nodes allocated: %,d%n", nodeCount);
        System.out.printf("  Status:                 %s%n", 
                         nodeCount == expectedNodes ? "✓ PASS" : "✗ FAIL");
        System.out.println();
        System.out.printf("  Memory before:          %,d bytes%n", memoryBefore);
        System.out.printf("  Memory after:           %,d bytes%n", memoryAfter);
        System.out.printf("  Memory allocated:       %,d bytes%n", memoryUsed);
        System.out.printf("  Memory per node (avg):  %.2f bytes%n", 
                         (double)memoryUsed / nodeCount);
        System.out.printf("  Time taken:             %.3f ms%n", timeTaken);
        System.out.println("============================================================");
    }
}

/**
 * Perfect Binary Tree Allocator
 */
public class BinaryTreeMemory {
    
    private AllocationStats stats;
    private MemoryMXBean memoryBean;
    private Runtime runtime;
    
    public BinaryTreeMemory() {
        this.stats = new AllocationStats();
        this.memoryBean = ManagementFactory.getMemoryMXBean();
        this.runtime = Runtime.getRuntime();
    }
    
    /**
     * MAIN ALGORITHM: Recursive allocation of perfect binary tree
     * 
     * Algorithm:
     * 1. Base case: if current_depth > target_depth, return null
     * 2. Allocate new TreeNode with current value
     * 3. Calculate child values (binary heap indexing)
     * 4. Recursively allocate left subtree at depth+1
     * 5. Recursively allocate right subtree at depth+1
     * 6. Return allocated node
     * 
     * Time Complexity: O(2^N) where N is depth
     * Space Complexity: O(2^N) for nodes + O(N) for recursion stack
     * 
     * @param currentDepth Current depth in tree
     * @param targetDepth Target depth for tree
     * @param nodeValue Value to assign to node
     * @return Allocated TreeNode or null
     */
    private TreeNode allocatePerfectTree(int currentDepth, int targetDepth, int nodeValue) {
        // Base case: exceeded target depth
        if (currentDepth > targetDepth) {
            return null;
        }
        
        // Allocate new node on heap
        TreeNode node = new TreeNode(nodeValue);
        stats.nodeCount++;
        
        // Calculate child values using binary heap indexing
        int leftValue = 2 * nodeValue + 1;
        int rightValue = 2 * nodeValue + 2;
        
        // Recursively allocate left and right subtrees
        node.left = allocatePerfectTree(currentDepth + 1, targetDepth, leftValue);
        node.right = allocatePerfectTree(currentDepth + 1, targetDepth, rightValue);
        
        return node;
    }
    
    /**
     * Calculate expected number of nodes
     */
    private long calculateExpectedNodes(int depth) {
        return (1L << (depth + 1)) - 1;
    }
    
    /**
     * Calculate actual tree depth
     */
    private int calculateTreeDepth(TreeNode node) {
        if (node == null) {
            return -1;
        }
        
        int leftDepth = calculateTreeDepth(node.left);
        int rightDepth = calculateTreeDepth(node.right);
        
        return 1 + Math.max(leftDepth, rightDepth);
    }
    
    /**
     * Get current heap memory usage
     */
    private long getUsedMemory() {
        MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();
        return heapUsage.getUsed();
    }
    
    /**
     * Traverse tree in preorder (limited display)
     */
    private void traversePreorder(TreeNode node, int depth, int maxDepth) {
        if (node == null || depth > maxDepth) {
            return;
        }
        
        // Print indentation
        for (int i = 0; i < depth; i++) {
            System.out.print("  ");
        }
        
        System.out.printf("Node(value=%d, depth=%d)%n", node.value, depth);
        
        traversePreorder(node.left, depth + 1, maxDepth);
        traversePreorder(node.right, depth + 1, maxDepth);
    }
    
    /**
     * Main allocation method with memory tracking
     */
    public TreeNode allocateTree(int depth) {
        System.out.println();
        System.out.println("============================================================");
        System.out.printf("Allocating Perfect Binary Tree - Depth: %d%n", depth);
        System.out.printf("Expected nodes: %,d%n", calculateExpectedNodes(depth));
        System.out.println("============================================================");
        
        // Reset statistics
        stats.reset();
        
        // Suggest GC before measurement (but don't force it)
        System.gc();
        try {
            Thread.sleep(100); // Give GC time to run
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        // Capture memory before allocation
        stats.memoryBefore = getUsedMemory();
        stats.startTime = System.currentTimeMillis();
        
        // ALLOCATE TREE - All nodes will be on heap before GC
        System.out.println("\nAllocating tree nodes...");
        TreeNode root = allocatePerfectTree(0, depth, 0);
        
        // Capture memory and time after allocation
        stats.endTime = System.currentTimeMillis();
        stats.memoryAfter = getUsedMemory();
        
        return root;
    }
    
    /**
     * Verify tree structure
     */
    public void verifyTree(TreeNode root, int expectedDepth) {
        int actualDepth = calculateTreeDepth(root);
        
        System.out.println("\nTree Verification:");
        System.out.printf("  Actual depth:   %d%n", actualDepth);
        System.out.printf("  Expected depth: %d%n", expectedDepth);
        System.out.printf("  Depth check:    %s%n", 
                         actualDepth == expectedDepth ? "✓ PASS" : "✗ FAIL");
    }
    
    /**
     * Display tree structure
     */
    public void displayTree(TreeNode root, int depth) {
        if (depth <= 4) {
            System.out.println("\nTree Structure (Preorder Traversal):");
            System.out.println("============================================================");
            traversePreorder(root, 0, depth);
        }
    }
    
    /**
     * Main execution method
     */
    public static void main(String[] args) {
        System.out.println("Perfect Binary Tree Memory Allocator (Java Implementation)");
        System.out.println("Using native Java heap management and Runtime API");
        System.out.println("============================================================");
        
        BinaryTreeMemory allocator = new BinaryTreeMemory();
        
        int[] depths = {3, 5, 8, 10, 12};
        
        for (int depth : depths) {
            System.out.println();
            System.out.println("############################################################");
            System.out.printf("# Testing with Depth = %d%n", depth);
            System.out.println("############################################################");
            
            // Allocate tree
            TreeNode root = allocator.allocateTree(depth);
            
            // Verify structure
            allocator.verifyTree(root, depth);
            
            // Print statistics
            allocator.stats.printStats(depth);
            
            // Display tree for small depths
            allocator.displayTree(root, depth);
            
            // IMPORTANT: Tree is fully in memory here
            System.out.println();
            System.out.printf("⚠️  ALL %,d NODES ARE CURRENTLY IN HEAP MEMORY%n", 
                             allocator.stats.nodeCount);
            System.out.println("   Nodes remain allocated until GC runs");
            
            // Cleanup
            System.out.println();
            System.out.println("============================================================");
            System.out.println("Cleanup Phase");
            System.out.println("============================================================");
            System.out.printf("  Dereferencing root (removing %,d node references)...%n", 
                             allocator.stats.nodeCount);
            
            // Remove reference to allow GC
            root = null;
            
            System.out.println("  ✓ Root dereferenced");
            System.out.println("  ✓ Nodes eligible for garbage collection");
            
            // Suggest garbage collection
            System.out.println("  Suggesting GC...");
            System.gc();
            
            System.out.printf("%n✓ Test completed for depth %d%n", depth);
            
            // Brief pause between tests
            try {
                Thread.sleep(200);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        System.out.println();
        System.out.println("============================================================");
        System.out.println("All tests completed successfully!");
        System.out.println("============================================================");
    }
}

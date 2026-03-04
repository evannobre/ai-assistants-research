import java.io.IOException;

/**
 * Implements the "Binary Trees" memory benchmark.
 * This adheres to the constraints: uses standard Java GC, 
 * a single node type, and the required allocation sequence.
 * * To run:
 * 1. Compile: javac BinaryTrees.java
 * 2. Run: java BinaryTrees 21
 */
public class BinaryTrees {

    // --- 1. Define a tree node class and methods ---
    /**
     * Tree node class. Leaf nodes are just interior nodes with null children.
     * This ensures the "same memory allocation" constraint for all nodes.
     */
    static final class Node {
        final Node left;
        final Node right;

        // An arbitrary value field to ensure the object is not a trivial size.
        // It's part of the node's allocation.
        final int item; 

        // Constructor for a node with children
        Node(Node left, Node right) {
            this.left = left;
            this.right = right;
            this.item = 0; // Default value
        }

        // Constructor for a leaf node (left and right are implicitly null)
        Node(int item) {
            this.left = null;
            this.right = null;
            this.item = item;
        }

        /**
         * The required algorithm for building a perfect binary tree, bottom-up.
         * Depth is the remaining depth to build.
         */
        static Node bottomUpTree(int depth) {
            if (depth > 0) {
                // Recursive call to build children
                // This is where per-node allocation occurs using 'new' (Java's native allocation)
                Node left = bottomUpTree(depth - 1);
                Node right = bottomUpTree(depth - 1);
                return new Node(left, right);
            } else {
                // Base case: leaf node
                return new Node(0); // Leaf node allocation
            }
        }

        /**
         * Walk the tree and count nodes, as required.
         */
        static int itemCheck(Node node) {
            if (node.left == null) {
                // Base case: leaf node. The 'item' check is arbitrary for the benchmark.
                return 1 + node.item; 
            } else {
                // Recursive case: interior node. 
                return 1 + itemCheck(node.left) + itemCheck(node.right);
            }
        }
    }

    // --- Core Benchmarking Logic ---

    /**
     * Executes the main allocation, walk, and deallocation loop.
     */
    private static void loopBottomUp(int depth, int iterations) {
        int check = 0;
        
        // Allocate, walk, and deallocate many bottom-up binary trees
        for (int i = 0; i < iterations; i++) {
            // Allocate a tree (many nodes allocated via recursion)
            Node tree = Node.bottomUpTree(depth);
            
            // Walk the tree, counting the nodes
            check += Node.itemCheck(tree);
            
            // Deallocate the tree. In Java, this is done by setting the reference 
            // to null, making the tree eligible for Garbage Collection (GC). 
            // We rely on the *default GC* to handle the deallocation.
            tree = null; 
        }

        // Print the final check sum
        System.out.printf("%d\t trees of depth %d\t check: %d\n", iterations, depth, check);
    }
    
    /**
     * Calculates the number of nodes in a perfect binary tree of a given depth.
     * A perfect tree of depth D has $2^{(D+1)} - 1$ nodes.
     */
    private static int nodesInTree(int depth) {
        return (1 << (depth + 1)) - 1;
    }

    public static void main(String[] args) throws IOException {
        int minDepth = 4; // Required minimum depth for allocation count analysis
        int N = 0; // Command line argument

        if (args.length > 0) {
            try {
                // Use a larger command line argument (21)
                N = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                // Fallback or error handling
            }
        }
        
        // Ensure the depth is at least the minimum required depth
        if (N < minDepth) N = minDepth;
        
        // The maximum depth to test
        int maxDepth = N;

        System.out.println("Starting Binary Trees Benchmark with Max Depth: " + maxDepth);
        System.out.println("------------------------------------------------------------------");


        // --- 2. Allocate a binary tree to "stretch" memory, check it exists, and deallocate it; ---
        // This acts as a warm-up, forcing initial memory allocation and potential first GC cycle.
        int stretchDepth = maxDepth + 1; // Stretch deeper than the main test set.
        int stretchCheck = 0;

        // Allocation 1: Stretch tree.
        System.out.printf("Stretch tree of depth %d\t check: ", stretchDepth);
        Node stretchTree = Node.bottomUpTree(stretchDepth);
        stretchCheck = Node.itemCheck(stretchTree);
        System.out.println(stretchCheck);
        
        // Deallocate the stretch tree by nulling the reference.
        // It's now eligible for GC (first 'deallocation').
        stretchTree = null; 
        // We rely on the JVM's *default GC* to free this memory later.
        
        System.out.println("------------------------------------------------------------------");


        // --- 3. Allocate a long-lived binary tree which will live-on while other trees are allocated and deallocated; ---
        // The longLivedTree will force the GC to potentially promote its nodes to an older generation 
        // while the younger trees are repeatedly created and collected.
        int longLivedDepth = maxDepth;
        
        // Allocation 2: Long-lived tree.
        Node longLivedTree = Node.bottomUpTree(longLivedDepth);
        // This tree *must not* be GC'd until the end check, so its reference is kept.
        
        System.out.printf("Long-lived tree of depth %d allocated. Check: %d\n", 
                          longLivedDepth, Node.itemCheck(longLivedTree));
        System.out.println("------------------------------------------------------------------");
        

        // --- 4. Allocate, walk, and deallocate many bottom-up binary trees: ---
        // This is the main performance loop.
        for (int depth = minDepth; depth <= maxDepth; depth += 2) {
            int iterations = 1 << (maxDepth - depth + minDepth); 
            
            // Allocation 3 and subsequent: Many short-lived trees.
            loopBottomUp(depth, iterations);
        }

        System.out.println("------------------------------------------------------------------");

        
        // --- 5. Check that the long-lived binary tree still exists. ---
        // We check its item count again to prove it was not GC'd during the loop.
        // Allocation 4: The final check relies on the long-lived tree remaining in memory.
        int finalCheck = Node.itemCheck(longLivedTree);
        System.out.printf("Long-lived tree of depth %d\t final check: %d\n", longLivedDepth, finalCheck);
        
        // Deallocate the long-lived tree by nulling the reference for completeness.
        longLivedTree = null;
        
        System.out.println("Benchmark Complete.");
    }
}
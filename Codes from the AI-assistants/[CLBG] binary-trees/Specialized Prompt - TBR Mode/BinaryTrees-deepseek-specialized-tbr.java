public class BinaryTreeBenchmark {
    
    static class TreeNode {
        TreeNode left;
        TreeNode right;
        
        TreeNode(TreeNode left, TreeNode right) {
            this.left = left;
            this.right = right;
        }
    }
    
    // Create a perfect binary tree of given depth
    private static TreeNode createTree(int depth) {
        if (depth <= 0) {
            return new TreeNode(null, null);
        }
        TreeNode left = createTree(depth - 1);
        TreeNode right = createTree(depth - 1);
        return new TreeNode(left, right);
    }
    
    // Count nodes in the tree
    private static int countNodes(TreeNode node) {
        if (node == null) {
            return 0;
        }
        return 1 + countNodes(node.left) + countNodes(node.right);
    }
    
    // Check tree structure is correct
    private static boolean verifyTreeStructure(TreeNode node, int currentDepth, int maxDepth) {
        if (node == null) {
            return false;
        }
        
        if (currentDepth == maxDepth) {
            // Should be a leaf node
            return node.left == null && node.right == null;
        } else {
            // Should be an interior node with both children
            return node.left != null && node.right != null &&
                   verifyTreeStructure(node.left, currentDepth + 1, maxDepth) &&
                   verifyTreeStructure(node.right, currentDepth + 1, maxDepth);
        }
    }
    
    public static void main(String[] args) {
        int depth = 21; // Default depth as specified
        
        // Use command line argument if provided
        if (args.length > 0) {
            try {
                depth = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                System.err.println("Invalid depth argument, using default: " + depth);
            }
        }
        
        System.out.println("Running binary tree benchmark with depth: " + depth);
        
        // 1. Allocate stretch tree (depth + 1), check it, and deallocate it
        System.gc(); // Suggest GC before starting
        long startTime = System.currentTimeMillis();
        
        System.out.println("Creating stretch tree (depth " + (depth + 1) + ")...");
        TreeNode stretchTree = createTree(depth + 1);
        
        // Verify stretch tree exists and has correct structure
        int stretchCount = countNodes(stretchTree);
        boolean stretchValid = verifyTreeStructure(stretchTree, 0, depth + 1);
        int expectedStretchNodes = (1 << (depth + 2)) - 1; // 2^(depth+2) - 1
        
        System.out.println("Stretch tree - Nodes: " + stretchCount + 
                          ", Expected: " + expectedStretchNodes + 
                          ", Valid: " + stretchValid);
        
        // Deallocate stretch tree
        stretchTree = null;
        System.gc(); // Suggest GC to collect stretch tree
        
        // 2. Create long-lived tree
        System.out.println("Creating long-lived tree (depth " + depth + ")...");
        TreeNode longLivedTree = createTree(depth);
        int longLivedCount = countNodes(longLivedTree);
        boolean longLivedValid = verifyTreeStructure(longLivedTree, 0, depth);
        int expectedLongLivedNodes = (1 << (depth + 1)) - 1;
        
        System.out.println("Long-lived tree - Nodes: " + longLivedCount + 
                          ", Expected: " + expectedLongLivedNodes + 
                          ", Valid: " + longLivedValid);
        
        // 3. Allocate, walk, and deallocate many bottom-up binary trees
        int iterations = Math.max(4, depth / 2); // At least 4 allocations as specified
        System.out.println("Allocating, walking, and deallocating " + iterations + " trees...");
        
        int totalNodesProcessed = 0;
        
        for (int i = 0; i < iterations; i++) {
            // Allocate tree
            TreeNode tempTree = createTree(depth);
            
            // Walk tree and count nodes
            int nodeCount = countNodes(tempTree);
            totalNodesProcessed += nodeCount;
            
            // Verify structure
            boolean valid = verifyTreeStructure(tempTree, 0, depth);
            
            if (!valid) {
                System.err.println("ERROR: Tree structure invalid in iteration " + i);
            }
            
            // Deallocate tree
            tempTree = null;
            
            if ((i + 1) % 10 == 0) {
                System.out.println("Completed " + (i + 1) + " iterations...");
            }
        }
        
        // 4. Verify long-lived tree still exists and is unchanged
        System.gc(); // Suggest GC before final check
        
        int finalLongLivedCount = countNodes(longLivedTree);
        boolean finalLongLivedValid = verifyTreeStructure(longLivedTree, 0, depth);
        
        System.out.println("Final long-lived tree check - Nodes: " + finalLongLivedCount + 
                          ", Valid: " + finalLongLivedValid + 
                          ", Unchanged: " + (finalLongLivedCount == longLivedCount));
        
        if (finalLongLivedCount != longLivedCount) {
            System.err.println("ERROR: Long-lived tree was modified!");
        }
        
        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;
        
        System.out.println("\nBenchmark completed:");
        System.out.println("Total time: " + duration + " ms");
        System.out.println("Total nodes processed: " + totalNodesProcessed);
        System.out.println("Long-lived tree preserved: " + (finalLongLivedCount == longLivedCount));
        
        // Memory usage info
        Runtime runtime = Runtime.getRuntime();
        long usedMemory = runtime.totalMemory() - runtime.freeMemory();
        System.out.println("Memory used: " + (usedMemory / (1024 * 1024)) + " MB");
    }
}
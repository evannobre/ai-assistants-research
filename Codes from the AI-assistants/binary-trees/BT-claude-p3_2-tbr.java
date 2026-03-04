/**
 * Binary Trees Benchmark - Java Implementation
 * Allocates and deallocates many binary trees using Java's native GC.
 * 
 * Compile: javac BinaryTrees.java
 * Run: java BinaryTrees <max_depth>
 * Example: java BinaryTrees 21
 */

public class BinaryTrees {
    
    /**
     * Binary tree node with left and right children.
     * Interior nodes and leaf nodes use the same allocation.
     */
    private static class TreeNode {
        private TreeNode left;
        private TreeNode right;
        
        TreeNode(TreeNode left, TreeNode right) {
            this.left = left;
            this.right = right;
        }
    }
    
    /**
     * Create a binary tree of given depth.
     * @param depth The depth of the tree to create
     * @return The root node of the created tree
     */
    private static TreeNode makeTree(int depth) {
        if (depth > 0) {
            return new TreeNode(
                makeTree(depth - 1),
                makeTree(depth - 1)
            );
        } else {
            return new TreeNode(null, null);
        }
    }
    
    /**
     * Count nodes in the tree (walk the tree).
     * @param node The root node to start counting from
     * @return The total number of nodes in the tree
     */
    private static int checkTree(TreeNode node) {
        if (node.left == null) {
            return 1;
        } else {
            return 1 + checkTree(node.left) + checkTree(node.right);
        }
    }
    
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java BinaryTrees <max_depth>");
            System.out.println("Example: java BinaryTrees 21");
            System.exit(1);
        }
        
        int maxDepth = Integer.parseInt(args[0]);
        int minDepth = 4;
        
        int stretchDepth = maxDepth + 1;
        
        // Stretch memory - allocate and check a large tree, then let it be GC'd
        System.out.println("stretch tree of depth " + stretchDepth + 
                         "\t check: " + checkTree(makeTree(stretchDepth)));
        
        // Allocate long-lived tree that will survive while other trees are created/destroyed
        TreeNode longLivedTree = makeTree(maxDepth);
        
        // Allocate, walk, and deallocate many bottom-up binary trees
        for (int depth = minDepth; depth <= maxDepth; depth += 2) {
            int iterations = 1 << (maxDepth - depth + minDepth);
            int checkSum = 0;
            
            for (int i = 0; i < iterations; i++) {
                // Allocate tree
                TreeNode tempTree = makeTree(depth);
                // Walk tree and count nodes
                checkSum += checkTree(tempTree);
                // Tree automatically deallocated by GC when it goes out of scope
            }
            
            System.out.println(iterations + "\t trees of depth " + depth + 
                             "\t check: " + checkSum);
        }
        
        // Check that long-lived tree still exists
        System.out.println("long lived tree of depth " + maxDepth + 
                         "\t check: " + checkTree(longLivedTree));
    }
}

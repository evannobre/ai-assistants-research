public class BinaryTrees {
    private static final int MIN_DEPTH = 4;
    
    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 0;
        int maxDepth = Math.max(MIN_DEPTH + 2, n);
        int stretchDepth = maxDepth + 1;
        
        // Allocate stretch tree, check it exists, and deallocate it
        System.out.println("stretch tree of depth " + stretchDepth + 
                         "\t check: " + TreeNode.createAndCheck(stretchDepth));
        
        // Allocate long-lived tree
        TreeNode longLivedTree = TreeNode.create(maxDepth);
        
        // Allocate, walk, and deallocate many bottom-up binary trees
        int iterations = 1 << (maxDepth - MIN_DEPTH + 2);
        
        for (int depth = MIN_DEPTH; depth <= maxDepth; depth += 2) {
            int check = 0;
            
            for (int i = 1; i <= iterations; i++) {
                // Allocate tree
                TreeNode tree = TreeNode.create(depth);
                // Walk tree and count nodes
                check += tree.check();
                // Tree is deallocated when it goes out of scope (GC will handle it)
            }
            
            System.out.println((iterations * 2) + "\t trees of depth " + depth + 
                             "\t check: " + check);
            iterations /= 4;
        }
        
        // Check that long-lived tree still exists
        System.out.println("long lived tree of depth " + maxDepth + 
                         "\t check: " + longLivedTree.check());
        
        // Force garbage collection to demonstrate trees are being collected
        System.gc();
        try {
            Thread.sleep(100); // Give GC a moment
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    static class TreeNode {
        private TreeNode left;
        private TreeNode right;
        
        public TreeNode(TreeNode left, TreeNode right) {
            this.left = left;
            this.right = right;
        }
        
        // Create a perfect binary tree of specified depth
        public static TreeNode create(int depth) {
            if (depth > 0) {
                return new TreeNode(create(depth - 1), create(depth - 1));
            } else {
                return new TreeNode(null, null);
            }
        }
        
        // Check the tree structure and return node count
        public int check() {
            if (left == null && right == null) {
                return 1;
            }
            return 1 + left.check() + right.check();
        }
        
        // Create tree and immediately check it (for stretch tree)
        public static int createAndCheck(int depth) {
            TreeNode tree = create(depth);
            int result = tree.check();
            // Tree will be garbage collected
            return result;
        }
    }
}
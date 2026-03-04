public class BinaryTrees {
    
    private static class TreeNode {
        TreeNode left;
        TreeNode right;
        
        TreeNode(int depth) {
            if (depth > 0) {
                left = new TreeNode(depth - 1);
                right = new TreeNode(depth - 1);
            }
        }
        
        int check() {
            if (left == null) {
                return 1;
            }
            return 1 + left.check() + right.check();
        }
    }
    
    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 10;
        
        final int minDepth = 4;
        final int maxDepth = Math.max(minDepth + 2, n);
        final int stretchDepth = maxDepth + 1;
        
        // Stretch memory
        {
            TreeNode stretchTree = new TreeNode(stretchDepth);
            System.out.println("stretch tree of depth " + stretchDepth + 
                             "\t check: " + stretchTree.check());
        }
        
        // Create long-lived tree
        TreeNode longLivedTree = new TreeNode(maxDepth);
        
        // Allocate, walk, and deallocate many bottom-up trees
        for (int depth = minDepth; depth <= maxDepth; depth += 2) {
            final int iterations = 1 << (maxDepth - depth + minDepth);
            int check = 0;
            
            for (int i = 0; i < iterations; i++) {
                TreeNode tree = new TreeNode(depth);
                check += tree.check();
            }
            
            System.out.println(iterations + "\t trees of depth " + depth + 
                             "\t check: " + check);
        }
        
        // Check long-lived tree
        System.out.println("long lived tree of depth " + maxDepth + 
                         "\t check: " + longLivedTree.check());
    }
}

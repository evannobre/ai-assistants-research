public class BinaryTrees {
    
    // Define a tree node class where leaf nodes and interior nodes share the exact same allocation
    static class TreeNode {
        TreeNode left, right;

        TreeNode(TreeNode left, TreeNode right) {
            this.left = left;
            this.right = right;
        }
    }

    static TreeNode makeTree(int depth) {
        if (depth > 0) {
            return new TreeNode(makeTree(depth - 1), makeTree(depth - 1));
        } else {
            return new TreeNode(null, null);
        }
    }

    static int checkTree(TreeNode node) {
        if (node.left == null) {
            return 1;
        }
        return 1 + checkTree(node.left) + checkTree(node.right);
    }

    public static void main(String[] args) {
        // Use command line argument if provided, otherwise default to 21
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 21;
        int minDepth = 4;
        int maxDepth = Math.max(minDepth + 2, n);
        int stretchDepth = maxDepth + 1;

        // 1. Allocate stretch tree, check it, and let it be GC'd
        TreeNode stretchTree = makeTree(stretchDepth);
        System.out.println("stretch tree of depth " + stretchDepth + "\t check: " + checkTree(stretchTree));
        stretchTree = null; 

        // 2. Allocate long-lived tree
        TreeNode longLivedTree = makeTree(maxDepth);

        // 3. Allocate, walk, and deallocate many trees
        for (int depth = minDepth; depth <= maxDepth; depth += 2) {
            int iterations = 1 << (maxDepth - depth + minDepth);
            int check = 0;

            for (int i = 1; i <= iterations; i++) {
                // Tree is allocated, walked, and loses its reference to be GC'd
                check += checkTree(makeTree(depth));
            }
            System.out.println(iterations + "\t trees of depth " + depth + "\t check: " + check);
        }

        // 4. Check that the long-lived tree still exists
        System.out.println("long lived tree of depth " + maxDepth + "\t check: " + checkTree(longLivedTree));
    }
}
public class BinaryTrees {

    private static final int MIN_DEPTH = 4;

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 21;
        int maxDepth = Math.max(MIN_DEPTH + 2, n);
        int stretchDepth = maxDepth + 1;

        // 1. Stretch memory: Allocate, check, and let GC reclaim
        checkTree("stretch tree", stretchDepth, createTree(stretchDepth));

        // 2. Long-lived tree: This lives until the end of the program
        TreeNode longLivedTree = createTree(maxDepth);

        // 3. Process many bottom-up trees of varying depths
        for (int depth = MIN_DEPTH; depth <= maxDepth; depth += 2) {
            int iterations = 1 << (maxDepth - depth + MIN_DEPTH);
            int check = 0;

            for (int i = 1; i <= iterations; i++) {
                check += checkTree(createTree(depth));
            }
            System.out.println(iterations + "\t trees of depth " + depth + "\t check: " + check);
        }

        // 4. Final check on the long-lived tree
        checkTree("long lived tree", maxDepth, longLivedTree);
    }

    // Standard Tree Node definition
    private static class TreeNode {
        private TreeNode left, right;

        TreeNode(TreeNode left, TreeNode right) {
            this.left = left;
            this.right = right;
        }
    }

    // Recursive allocation (Bottom-up)
    private static TreeNode createTree(int depth) {
        if (depth > 0) {
            return new TreeNode(createTree(depth - 1), createTree(depth - 1));
        } else {
            return new TreeNode(null, null); // Leaf nodes are same allocation
        }
    }

    // Walk the tree and count nodes
    private static int checkTree(TreeNode node) {
        if (node.left == null) return 1;
        return 1 + checkTree(node.left) + checkTree(node.right);
    }

    // Helper for printing
    private static void checkTree(String name, int depth, TreeNode tree) {
        System.out.println(name + " of depth " + depth + "\t check: " + checkTree(tree));
    }
}
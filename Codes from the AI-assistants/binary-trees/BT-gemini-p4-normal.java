import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class BinaryTrees {

    private static final int MIN_DEPTH = 4;

    public static void main(String[] args) throws InterruptedException {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 21;
        int maxDepth = Math.max(MIN_DEPTH + 2, n);
        int stretchDepth = maxDepth + 1;

        // 1. Stretch memory
        System.out.println("stretch tree of depth " + stretchDepth + "\t check: " 
            + checkTree(createTree(stretchDepth)));

        // 2. Create long-lived tree
        TreeNode longLivedTree = createTree(maxDepth);

        // 3. Process trees of varying depths in a loop (bottom-up)
        for (int depth = MIN_DEPTH; depth <= maxDepth; depth += 2) {
            int iterations = 1 << (maxDepth - depth + MIN_DEPTH);
            int check = 0;

            for (int i = 1; i <= iterations; i++) {
                check += checkTree(createTree(depth));
            }
            System.out.println(iterations + "\t trees of depth " + depth + "\t check: " + check);
        }

        // 4. Verify long-lived tree still exists
        System.out.println("long lived tree of depth " + maxDepth + "\t check: " 
            + checkTree(longLivedTree));
    }

    /**
     * Tree Node Definition
     * Per your requirements: leaf nodes and interior nodes use the same allocation.
     */
    private static class TreeNode {
        private TreeNode left, right;

        private TreeNode(TreeNode left, TreeNode right) {
            this.left = left;
            this.right = right;
        }
    }

    /**
     * Functional creation of a perfect binary tree.
     */
    private static TreeNode createTree(int depth) {
        if (depth > 0) {
            return new TreeNode(createTree(depth - 1), createTree(depth - 1));
        } else {
            return new TreeNode(null, null);
        }
    }

    /**
     * Tree walk to count nodes.
     */
    private static int checkTree(TreeNode node) {
        if (node.left == null) {
            return 1;
        }
        return 1 + checkTree(node.left) + checkTree(node.right);
    }
}
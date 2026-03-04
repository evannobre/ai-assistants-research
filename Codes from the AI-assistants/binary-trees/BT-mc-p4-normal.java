// File: BinaryTrees.java
public class BinaryTrees {

    private static final int MIN_DEPTH = 4;

    static final class TreeNode {
        private final TreeNode left;
        private final TreeNode right;
        private final int item;

        TreeNode(TreeNode left, TreeNode right, int item) {
            this.left = left;
            this.right = right;
            this.item = item;
        }

        static TreeNode bottomUpTree(int item, int depth) {
            if (depth > 0) {
                return new TreeNode(
                    bottomUpTree(2 * item - 1, depth - 1),
                    bottomUpTree(2 * item, depth - 1),
                    item
                );
            } else {
                // Leaf node uses the same allocation as interior nodes
                return new TreeNode(null, null, item);
            }
        }

        int itemCheck() {
            // Simple walk to ensure work is not optimized away
            if (left == null) {
                return item;
            }
            return item + left.itemCheck() - right.itemCheck();
        }
    }

    public static void main(String[] args) {
        int n = 21; // default if not provided
        if (args.length > 0) {
            n = Integer.parseInt(args[0]);
        }

        int maxDepth = Math.max(MIN_DEPTH + 2, n);
        int stretchDepth = maxDepth + 1;

        // Stretch tree: allocate, walk, then let it be GC'd
        {
            TreeNode stretchTree = TreeNode.bottomUpTree(0, stretchDepth);
            int check = stretchTree.itemCheck();
            System.out.println("stretch tree of depth " + stretchDepth + "\t check: " + check);
            // Deallocate by dropping reference; GC will reclaim later
            stretchTree = null;
        }

        // Long-lived tree
        TreeNode longLivedTree = TreeNode.bottomUpTree(0, maxDepth);

        // Allocate, walk, and deallocate many bottom-up trees
        for (int depth = MIN_DEPTH; depth <= maxDepth; depth += 2) {
            int iterations = 1 << (maxDepth - depth + MIN_DEPTH);
            int check = 0;

            for (int i = 1; i <= iterations; i++) {
                // Positive item
                TreeNode t1 = TreeNode.bottomUpTree(i, depth);
                check += t1.itemCheck();
                // Deallocate t1 by losing reference
                t1 = null;

                // Negative item
                TreeNode t2 = TreeNode.bottomUpTree(-i, depth);
                check += t2.itemCheck();
                // Deallocate t2 by losing reference
                t2 = null;
            }

            System.out.println(
                iterations * 2 + "\t trees of depth " + depth + "\t check: " + check
            );
        }

        // Check that the long-lived tree still exists and is walkable
        int longLivedCheck = longLivedTree.itemCheck();
        System.out.println("long lived tree of depth " + maxDepth + "\t check: " + longLivedCheck);
    }
}

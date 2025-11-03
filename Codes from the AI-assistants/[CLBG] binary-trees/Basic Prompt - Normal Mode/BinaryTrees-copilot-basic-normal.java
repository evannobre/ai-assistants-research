public class BinaryTrees {
    static class TreeNode {
        TreeNode left, right;

        TreeNode(TreeNode left, TreeNode right) {
            this.left = left;
            this.right = right;
        }
    }

    static TreeNode makeTree(int depth) {
        if (depth <= 0) return new TreeNode(null, null);
        return new TreeNode(makeTree(depth - 1), makeTree(depth - 1));
    }

    static int checkTree(TreeNode node) {
        if (node.left == null && node.right == null) return 1;
        return 1 + checkTree(node.left) + checkTree(node.right);
    }

    public static void main(String[] args) {
        int maxDepth = (args.length > 0) ? Integer.parseInt(args[0]) : 21;
        int minDepth = 4;
        int stretchDepth = maxDepth + 1;

        // Stretch memory
        TreeNode stretchTree = makeTree(stretchDepth);
        System.out.println("stretch tree of depth " + stretchDepth + "\t check: " + checkTree(stretchTree));
        stretchTree = null;

        // Long-lived tree
        TreeNode longLivedTree = makeTree(maxDepth);

        for (int depth = minDepth; depth <= maxDepth; depth += 2) {
            int iterations = 1 << (maxDepth - depth + minDepth);
            int check = 0;
            for (int i = 0; i < iterations; i++) {
                TreeNode tree = makeTree(depth);
                check += checkTree(tree);
                tree = null;
            }
            System.out.println(iterations + "\t trees of depth " + depth + "\t check: " + check);
        }

        System.out.println("long lived tree of depth " + maxDepth + "\t check: " + checkTree(longLivedTree));
    }
}
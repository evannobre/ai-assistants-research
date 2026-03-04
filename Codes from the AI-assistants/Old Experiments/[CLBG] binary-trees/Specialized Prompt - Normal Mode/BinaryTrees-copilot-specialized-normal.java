public class BinaryTreeBenchmark {

    static class TreeNode {
        TreeNode left, right;

        TreeNode(TreeNode left, TreeNode right) {
            this.left = left;
            this.right = right;
        }

        static TreeNode create(int depth) {
            if (depth <= 0) return new TreeNode(null, null);
            return new TreeNode(create(depth - 1), create(depth - 1));
        }

        int countNodes() {
            if (left == null && right == null) return 1;
            return 1 + left.countNodes() + right.countNodes();
        }
    }

    public static void main(String[] args) {
        int maxDepth = (args.length > 0) ? Integer.parseInt(args[0]) : 21;
        int minDepth = 4;
        int stretchDepth = maxDepth + 1;

        // Stretch memory
        TreeNode stretchTree = TreeNode.create(stretchDepth);
        System.out.println("Stretch tree of depth " + stretchDepth + " has " + stretchTree.countNodes() + " nodes");
        stretchTree = null;

        // Long-lived tree
        TreeNode longLivedTree = TreeNode.create(maxDepth);

        // Allocate many trees
        for (int depth = minDepth; depth <= maxDepth; depth += 2) {
            int iterations = 1 << (maxDepth - depth + minDepth);
            int totalNodes = 0;

            for (int i = 0; i < iterations; i++) {
                TreeNode tree = TreeNode.create(depth);
                totalNodes += tree.countNodes();
                tree = null;
            }

            System.out.println(iterations + " trees of depth " + depth + " have " + totalNodes + " nodes");
        }

        // Validate long-lived tree
        System.out.println("Long-lived tree of depth " + maxDepth + " has " + longLivedTree.countNodes() + " nodes");
    }
}
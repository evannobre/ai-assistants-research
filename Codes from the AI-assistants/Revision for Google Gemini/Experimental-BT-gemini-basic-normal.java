public class BinaryTrees {

    // 1. Native class relying on the JVM's memory allocator
    static class TreeNode {
        TreeNode left, right;

        TreeNode(TreeNode left, TreeNode right) {
            this.left = left;
            this.right = right;
        }
    }

    // 2. Recursively create a perfect binary tree of a given depth
    static TreeNode createTree(int depth) {
        if (depth == 0) {
            return new TreeNode(null, null); // Leaf node
        }
        // Allocates nodes rapidly on the heap
        return new TreeNode(createTree(depth - 1), createTree(depth - 1));
    }

    // 3. Traverse the tree to verify its integrity (counts the nodes)
    static int checkTree(TreeNode node) {
        if (node.left == null) {
            return 1;
        }
        return 1 + checkTree(node.left) + checkTree(node.right);
    }

    public static void main(String[] args) {
        // N is the target depth (defaulting to 10 for demonstration)
        int n = (args.length > 0) ? Integer.parseInt(args[0]) : 10;
        int minDepth = 4;
        int maxDepth = Math.max(minDepth + 2, n);
        int stretchDepth = maxDepth + 1;

        // PHASE 1: The "Stretch" Tree
        // Allocated and immediately lost from scope to trigger early GC
        int stretchCheck = checkTree(createTree(stretchDepth));
        System.out.println("stretch tree of depth " + stretchDepth + "\t check: " + stretchCheck);

        // PHASE 2: The Long-Lived Tree
        // Allocated BEFORE the massive memory churn. We hold the reference 
        // in 'longLivedTree' so the Garbage Collector cannot reclaim it.
        TreeNode longLivedTree = createTree(maxDepth);

        // PHASE 3: The Short-Lived Trees (The Churn)
        for (int depth = minDepth; depth <= maxDepth; depth += 2) {
            int iterations = 1 << (maxDepth - depth + minDepth);
            int check = 0;

            // Millions of nodes are allocated and immediately orphaned here,
            // forcing the GC to work overtime while dodging the longLivedTree.
            for (int i = 1; i <= iterations; i++) {
                check += checkTree(createTree(depth));
            }
            System.out.println(iterations + "\t trees of depth " + depth + "\t check: " + check);
        }

        // PHASE 4: Verification
        // Prove the long-lived tree survived the garbage collection cycles
        System.out.println("long lived tree of depth " + maxDepth + "\t check: " + checkTree(longLivedTree));
    }
}
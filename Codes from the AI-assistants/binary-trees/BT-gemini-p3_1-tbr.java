/*
 * Binary Trees Benchmark - Java
 * Uses default JVM Garbage Collection.
 * * Usage: java BinaryTrees 21
 */

public class BinaryTrees {

    // 1. Define a tree node class
    private static class TreeNode {
        private final TreeNode left;
        private final TreeNode right;

        // Leaf nodes are the same as interior nodes (same allocation)
        private TreeNode(TreeNode left, TreeNode right) {
            this.left = left;
            this.right = right;
        }

        // 2. Recursive allocation (bottom-up)
        private static TreeNode create(int depth) {
            if (depth == 0) {
                return new TreeNode(null, null);
            }
            return new TreeNode(create(depth - 1), create(depth - 1));
        }

        // Walk the tree, counting nodes
        private int itemCheck() {
            // If left is null, right is also null (perfect binary tree)
            if (left == null) {
                return 1;
            }
            return 1 + left.itemCheck() + right.itemCheck();
        }
    }

    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 21;
        int minDepth = 4;
        
        // Ensure maxDepth is at least minDepth + 2
        int maxDepth = (minDepth + 2 > n) ? minDepth + 2 : n;
        int stretchDepth = maxDepth + 1;

        // 3. Allocate "Stretch" Tree (depth + 1), check, and deallocate (let GC handle it)
        System.out.println("stretch tree of depth " + stretchDepth + "\t check: " 
                + TreeNode.create(stretchDepth).itemCheck());

        // 4. Allocate Long-Lived Tree
        TreeNode longLivedTree = TreeNode.create(maxDepth);

        // 5. Allocate, walk, and deallocate many bottom-up binary trees
        for (int depth = minDepth; depth <= maxDepth; depth += 2) {
            int iterations = 1 << (maxDepth - depth + minDepth);
            int check = 0;

            for (int i = 1; i <= iterations; i++) {
                // Allocation happens inside create()
                // Deallocation happens implicitly when 'temp' goes out of scope and GC runs
                TreeNode temp = TreeNode.create(depth);
                check += temp.itemCheck();
            }
            
            System.out.println(iterations + "\t trees of depth " + depth + "\t check: " + check);
        }

        // 6. Check that the long-lived binary tree still exists
        System.out.println("long lived tree of depth " + maxDepth + "\t check: " 
                + longLivedTree.itemCheck());
    }
}
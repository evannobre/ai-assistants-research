// BinaryTrees.java
// Classic binary-trees benchmark implemented for Java (uses default GC and standard libraries)

public class BinaryTrees {

    // Single node class used for leaves and interior nodes.
    // Both leaf and interior nodes are instances of this same class.
    private static final class Node {
        Node left;
        Node right;

        Node(Node left, Node right) {
            this.left = left;
            this.right = right;
        }
    }

    // Construct a perfect binary tree of given depth, bottom-up
    private static Node makeTree(int depth) {
        if (depth <= 0) {
            return new Node(null, null);
        }
        Node left = makeTree(depth - 1);
        Node right = makeTree(depth - 1);
        return new Node(left, right);
    }

    // Count nodes by traversing the tree
    private static int checkTree(Node node) {
        if (node.left == null && node.right == null) return 1;
        // Both children exist in our construction above for depth>0
        return 1 + checkTree(node.left) + checkTree(node.right);
    }

    // Main benchmark flow
    public static void main(String[] args) {
        int n = 21; // default depth
        if (args.length > 0) {
            try {
                n = Integer.parseInt(args[0]);
            } catch (NumberFormatException ex) {
                System.err.println("Argument must be an integer; using 21");
                n = 21;
            }
        }

        final int maxDepth = Math.max(4, n);
        final int stretchDepth = maxDepth + 1;

        // 1) Stretch tree to allocate and free a large tree immediately
        {
            Node stretchTree = makeTree(stretchDepth);
            int c = checkTree(stretchTree);
            System.out.println("stretch tree of depth " + stretchDepth + "\t check: " + c);
            stretchTree = null; // eligible for GC
        }

        // 2) Long-lived tree that will remain allocated
        Node longLivedTree = makeTree(maxDepth);

        // 3) Nested loops creating many trees of varying depths
        for (int depth = 4; depth <= maxDepth; depth += 2) {
            final int iterations = 1 << (maxDepth - depth + 2); // scale factor used in classic benchmark
            int totalCheck = 0;
            for (int i = 0; i < iterations; i++) {
                Node t = makeTree(depth);
                totalCheck += checkTree(t);
                // let local reference go out of scope to allow GC to reclaim
                t = null;
            }
            System.out.println((iterations) + "\t trees of depth " + depth + "\t check: " + totalCheck);
        }

        // 4) Check that the long-lived tree is still intact
        int longLivedCheck = checkTree(longLivedTree);
        System.out.println("long lived tree of depth " + maxDepth + "\t check: " + longLivedCheck);
    }
}
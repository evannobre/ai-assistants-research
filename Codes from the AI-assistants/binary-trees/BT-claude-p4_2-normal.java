public class BinaryTrees {
    
    // Tree node class - same for leaf and interior nodes
    static class Node {
        Node left;
        Node right;
        
        Node(Node left, Node right) {
            this.left = left;
            this.right = right;
        }
    }
    
    // Create a tree of given depth
    static Node createTree(int depth) {
        if (depth == 0) {
            return new Node(null, null);
        }
        return new Node(createTree(depth - 1), createTree(depth - 1));
    }
    
    // Check tree exists by counting nodes
    static int checkTree(Node node) {
        if (node.left == null) {
            return 1;
        }
        return 1 + checkTree(node.left) + checkTree(node.right);
    }
    
    public static void main(String[] args) {
        int n = args.length > 0 ? Integer.parseInt(args[0]) : 10;
        int minDepth = 4;
        int maxDepth = Math.max(minDepth + 2, n);
        int stretchDepth = maxDepth + 1;
        
        // Stretch memory - allocate and deallocate
        {
            Node stretchTree = createTree(stretchDepth);
            System.out.println("stretch tree of depth " + stretchDepth + 
                             "\t check: " + checkTree(stretchTree));
        }
        
        // Allocate long-lived tree
        Node longLivedTree = createTree(maxDepth);
        
        // Allocate, walk, and deallocate many bottom-up trees
        for (int depth = minDepth; depth <= maxDepth; depth += 2) {
            int iterations = 1 << (maxDepth - depth + minDepth);
            int check = 0;
            
            for (int i = 1; i <= iterations; i++) {
                Node tree = createTree(depth);
                check += checkTree(tree);
            }
            
            System.out.println(iterations + "\t trees of depth " + depth + 
                             "\t check: " + check);
        }
        
        // Check long-lived tree still exists
        System.out.println("long lived tree of depth " + maxDepth + 
                         "\t check: " + checkTree(longLivedTree));
    }
}

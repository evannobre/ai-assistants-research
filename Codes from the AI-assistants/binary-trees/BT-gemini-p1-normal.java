public class TreeSimulation {
    
    // Simple Node structure
    static class Node {
        Node left;
        Node right;
        int value;

        Node(int value) {
            this.value = value;
        }
    }

    public static Node createPerfectTree(int depth) {
        if (depth < 0) return null;

        Node node = new Node(depth);
        node.left = createPerfectTree(depth - 1);
        node.right = createPerfectTree(depth - 1);
        return node;
    }

    public static void main(String[] args) {
        int N = 20; // Adjust based on your available RAM
        System.out.println("Allocating a perfect binary tree of depth: " + N);
        
        long startTime = System.currentTimeMillis();
        
        // The 'root' reference keeps the entire tree reachable, 
        // preventing GC from reclaiming nodes during construction.
        Node root = createPerfectTree(N);
        
        long endTime = System.currentTimeMillis();
        
        System.out.println("Tree built successfully with " + ((1 << (N + 1)) - 1) + " nodes.");
        System.out.println("Time taken: " + (endTime - startTime) + "ms");
        
        // Optional: Keep root alive for a bit to inspect memory
        // System.out.println("Root node hash: " + root.hashCode());
    }
}
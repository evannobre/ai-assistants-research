import java.util.*;

/**
 * High-Performance Perfect Binary Tree Generator
 * Optimized for Ubuntu 24.04 64-bit / 8GB RAM
 */
public class BinaryTreeEngine {

    static class Node {
        long data;
        Node left, right;

        Node(long data) {
            this.data = data;
        }
    }

    public static void main(String[] args) {
        // N=25 is safe for 8GB RAM. N=26 targets ~4GB.
        int n = 25; 
        System.out.println("Starting allocation for depth: " + n);
        
        long startTime = System.currentTimeMillis();
        
        // Use a Deque for Level-Order construction (Breadth-First)
        // This ensures the tree is built layer by layer natively.
        Node root = createPerfectTree(n);
        
        long endTime = System.currentTimeMillis();
        
        System.out.println("Tree built successfully.");
        System.out.println("Time taken: " + (endTime - startTime) + "ms");
        
        // Keep reference alive to prevent GC during measurement
        System.out.println("Root Hash: " + root.hashCode());
    }

    public static Node createPerfectTree(int depth) {
        if (depth < 0) return null;

        Node root = new Node(0);
        Queue<Node> queue = new ArrayDeque<>(1 << (depth)); // Native pre-sized queue
        queue.add(root);

        for (int d = 0; d < depth; d++) {
            int levelSize = queue.size();
            for (int i = 0; i < levelSize; i++) {
                Node current = queue.poll();
                
                current.left = new Node(i * 2);
                current.right = new Node(i * 2 + 1);
                
                queue.add(current.left);
                queue.add(current.right);
            }
        }
        return root;
    }
}
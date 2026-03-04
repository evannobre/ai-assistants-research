import java.util.LinkedList;
import java.util.Queue;

class TreeNode {
    int value;
    int level;
    TreeNode left;
    TreeNode right;
    
    TreeNode(int value, int level) {
        this.value = value;
        this.level = level;
        this.left = null;
        this.right = null;
    }
}

public class BinaryTreeBuilder {
    private static int nodeCounter = 0;
    
    public static TreeNode buildPerfectTree(int depth) {
        if (depth < 0) return null;
        
        nodeCounter = 0;
        TreeNode root = new TreeNode(nodeCounter++, 0);
        
        // Use Java's LinkedList as Queue (native collection)
        Queue<TreeNode> nodeQueue = new LinkedList<>();
        nodeQueue.offer(root);
        
        while (!nodeQueue.isEmpty()) {
            TreeNode current = nodeQueue.poll();
            
            if (current.level < depth) {
                // Allocate left child
                current.left = new TreeNode(nodeCounter++, current.level + 1);
                nodeQueue.offer(current.left);
                
                // Allocate right child
                current.right = new TreeNode(nodeCounter++, current.level + 1);
                nodeQueue.offer(current.right);
            }
        }
        
        return root;
    }
    
    public static void printTreeStats(int depth) {
        int expectedNodes = (int) Math.pow(2, depth + 1) - 1;
        System.out.println("Tree Statistics:");
        System.out.println("Depth: " + depth);
        System.out.println("Total Nodes Allocated: " + nodeCounter);
        System.out.println("Expected Nodes: " + expectedNodes);
    }
    
    public static void main(String[] args) {
        int depth = 10;
        
        System.out.println("Building perfect binary tree of depth " + depth + "...");
        TreeNode root = buildPerfectTree(depth);
        
        printTreeStats(depth);
        
        // Keep strong reference to prevent GC
        System.out.println("\nTree built successfully. Root reference held.");
        System.out.println("Root node value: " + root.value);
        
        // At this point, tree is fully allocated and referenced
        // GC won't collect it while root reference exists
        
        // Nullify to allow GC (simulating post-use)
        root = null;
        System.gc(); // Suggest GC (not guaranteed to run immediately)
        System.out.println("Root reference cleared. GC suggested.");
    }
}
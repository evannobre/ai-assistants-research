import java.lang.foreign.*;
import java.lang.invoke.MethodHandle;
import java.util.ArrayList;
import java.util.List;

public class PerfectBinaryTree {
    // Native memory segment for explicit memory management
    private static final MemorySegment nativeMemory = Arena.ofAuto().allocate(1024 * 1024);
    
    static class TreeNode {
        int value;
        TreeNode left;
        TreeNode right;
        
        TreeNode(int val) {
            this.value = val;
        }
    }
    
    public static TreeNode createPerfectBinaryTree(int depth) {
        if (depth <= 0) return null;
        
        // Use ArrayList to prevent GC of nodes
        List<TreeNode> allNodes = new ArrayList<>();
        
        // Create root
        TreeNode root = new TreeNode(1);
        allNodes.add(root);
        
        // Use queue for BFS construction
        List<TreeNode> currentLevel = new ArrayList<>();
        currentLevel.add(root);
        
        int nodeValue = 2;
        
        // Build level by level
        for (int level = 1; level < depth; level++) {
            List<TreeNode> nextLevel = new ArrayList<>();
            
            for (TreeNode parent : currentLevel) {
                // Create left child
                TreeNode leftChild = new TreeNode(nodeValue++);
                parent.left = leftChild;
                allNodes.add(leftChild);
                nextLevel.add(leftChild);
                
                // Create right child
                TreeNode rightChild = new TreeNode(nodeValue++);
                parent.right = rightChild;
                allNodes.add(rightChild);
                nextLevel.add(rightChild);
            }
            
            currentLevel = nextLevel;
        }
        
        // Force allocation and prevent GC
        System.gc(); // Suggest GC before measurement
        Runtime runtime = Runtime.getRuntime();
        long usedMemory = runtime.totalMemory() - runtime.freeMemory();
        System.out.println("Memory used: " + usedMemory / (1024 * 1024) + " MB");
        
        return root;
    }
    
    public static void main(String[] args) {
        int depth = 20; // Creates ~1 million nodes
        System.out.println("Creating perfect binary tree of depth: " + depth);
        
        TreeNode tree = createPerfectBinaryTree(depth);
        
        // Keep reference to prevent GC
        System.out.println("Tree created. Root value: " + tree.value);
        System.out.println("Total nodes: " + (Math.pow(2, depth) - 1));
    }
}
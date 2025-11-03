import java.util.LinkedList;
import java.util.Queue;

class TreeNode {
    TreeNode left;
    TreeNode right;
}

public class BalancedTree {
    
    public static TreeNode createBalancedTree(int depth) {
        if (depth <= 0) return null;
        
        TreeNode node = new TreeNode();
        node.left = createBalancedTree(depth - 1);
        node.right = createBalancedTree(depth - 1);
        
        return node;
    }
    
    public static TreeNode createBalancedTreeIterative(int depth) {
        if (depth <= 0) return null;
        
        TreeNode root = new TreeNode();
        Queue<TreeNode> currentLevel = new LinkedList<>();
        currentLevel.offer(root);
        
        for (int i = 1; i < depth; i++) {
            Queue<TreeNode> nextLevel = new LinkedList<>();
            while (!currentLevel.isEmpty()) {
                TreeNode node = currentLevel.poll();
                node.left = new TreeNode();
                node.right = new TreeNode();
                nextLevel.offer(node.left);
                nextLevel.offer(node.right);
            }
            currentLevel = nextLevel;
        }
        
        return root;
    }
    
    public static int countNodes(TreeNode root) {
        if (root == null) return 0;
        return 1 + countNodes(root.left) + countNodes(root.right);
    }
    
    public static void printTreeStructure(TreeNode root, int level) {
        if (root == null) return;
        
        System.out.println("  ".repeat(level) + "Node");
        printTreeStructure(root.left, level + 1);
        printTreeStructure(root.right, level + 1);
    }
    
    public static void main(String[] args) {
        int depth = 4;
        TreeNode root = createBalancedTree(depth);
        
        System.out.println("Created balanced tree with depth " + depth);
        System.out.println("Total nodes: " + countNodes(root));
        System.out.println("Expected nodes: " + (Math.pow(2, depth) - 1));
        
        System.out.println("\nTree structure:");
        printTreeStructure(root, 0);
    }
}
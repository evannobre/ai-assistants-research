import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.MemoryUsage;

public class BinaryTreeSimulation {

    // 1. Using a Java 'record' for native JVM memory optimization.
    // It creates an immutable, tightly packed memory structure automatically.
    record TreeNode(TreeNode left, TreeNode right) {
        
        // 2 & 3 & 4. Recursive Memory Allocation
        static TreeNode createTree(int depth) {
            if (depth == 0) {
                return new TreeNode(null, null); // Base case: Leaf node
            }
            // Because we pass the recursive calls directly into the constructor,
            // the JVM links the references instantly. No node is orphaned.
            return new TreeNode(createTree(depth - 1), createTree(depth - 1));
        }

        // 6. Native traversal to verify the memory block
        int check() {
            if (left == null) {
                return 1;
            }
            return 1 + left.check() + right.check();
        }
    }

    public static void main(String[] args) {
        int depth = 20; // 2^21 - 1 nodes (approx. 2.09 million objects)
        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        
        System.out.println("Starting memory allocation for depth: " + depth);
        long startTime = System.currentTimeMillis();

        // 5. ANCHOR THE ROOT
        // As long as 'root' exists in this method scope, the entire tree is strongly 
        // reachable. The GC cannot touch a single node while this builds.
        TreeNode root = TreeNode.createTree(depth);
        
        long endTime = System.currentTimeMillis();
        
        // Output allocation metrics
        MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();
        double usedMegabytes = heapUsage.getUsed() / (1024.0 * 1024.0);
        
        System.out.println("Tree constructed in " + (endTime - startTime) + " ms");
        System.out.printf("Estimated Heap Used: %.2f MB%n", usedMegabytes);
        System.out.println("Tree Checksum (Nodes): " + root.check());

        // 7. RELEASE AND COLLECT
        // By unlinking the root, the entire tree of 2.09 million nodes becomes 
        // instantly eligible for Garbage Collection.
        root = null; 
        
        System.out.println("Root nullified. Requesting native GC sweep...");
        System.gc(); // Native call to hint the JVM Garbage Collector
        
        heapUsage = memoryBean.getHeapMemoryUsage();
        System.out.printf("Heap Used Post-GC: %.2f MB%n", heapUsage.getUsed() / (1024.0 * 1024.0));
    }
}
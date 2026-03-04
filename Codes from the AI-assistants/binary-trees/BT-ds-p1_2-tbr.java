import sun.misc.Unsafe;
import java.lang.reflect.Field;

class OffHeapTree {
    private static final Unsafe unsafe;
    private static final long NODE_SIZE = 24; // 3 longs (id, left, right)
    private long memoryPool;
    private int nodeCount;
    
    static {
        try {
            Field field = Unsafe.class.getDeclaredField("theUnsafe");
            field.setAccessible(true);
            unsafe = (Unsafe) field.get(null);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
    
    public long buildTree(int depth) {
        nodeCount = (1 << depth) - 1;
        long totalBytes = nodeCount * NODE_SIZE;
        
        // Allocate off-heap memory
        memoryPool = unsafe.allocateMemory(totalBytes);
        
        // Build tree structure
        for (int i = 0; i < nodeCount; i++) {
            long nodeAddr = memoryPool + i * NODE_SIZE;
            
            // Store node ID
            unsafe.putLong(nodeAddr, i);
            
            // Set child pointers
            int leftIdx = 2 * i + 1;
            int rightIdx = 2 * i + 2;
            
            if (leftIdx < nodeCount) {
                unsafe.putLong(nodeAddr + 8, memoryPool + leftIdx * NODE_SIZE);
            }
            if (rightIdx < nodeCount) {
                unsafe.putLong(nodeAddr + 16, memoryPool + rightIdx * NODE_SIZE);
            }
        }
        
        return memoryPool; // Returns address of root
    }
}
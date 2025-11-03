import java.util.concurrent.*;
import java.util.*;

public class FannkuchRedux {
    private final int n;
    private final int totalPerms;
    
    public FannkuchRedux(int n) {
        this.n = n;
        this.totalPerms = factorial(n);
    }
    
    private static int factorial(int n) {
        int result = 1;
        for (int i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }
    
    private static class Result {
        int maxFlips;
        int checksum;
    }
    
    private Result processSlice(int start, int end) {
        int[] count = new int[n];
        int[] perm = new int[n];
        for (int i = 0; i < n; i++) {
            perm[i] = i;
        }
        
        Result result = new Result();
        
        // Skip to starting permutation
        for (int i = 0; i < start; i++) {
            int j = 1;
            while (j < n && count[j] >= j) {
                count[j] = 0;
                j++;
            }
            if (j >= n) break;
            count[j]++;
            reverse(perm, 0, j);
        }
        
        // Process the slice
        for (int idx = start; idx < end; idx++) {
            int first = perm[0];
            if (first > 0) {
                int flips = 0;
                int[] tempPerm = perm.clone();
                int k = first;
                
                while (k != 0) {
                    reverse(tempPerm, 0, k);
                    flips++;
                    k = tempPerm[0];
                }
                
                if (flips > result.maxFlips) {
                    result.maxFlips = flips;
                }
                
                result.checksum += (idx % 2 == 0) ? flips : -flips;
            }
            
            // Generate next permutation
            int j = 1;
            while (j < n && count[j] >= j) {
                count[j] = 0;
                j++;
            }
            if (j >= n) break;
            count[j]++;
            reverse(perm, 0, j);
        }
        
        return result;
    }
    
    private void reverse(int[] arr, int start, int end) {
        while (start < end) {
            int temp = arr[start];
            arr[start] = arr[end];
            arr[end] = temp;
            start++;
            end--;
        }
    }
    
    public int[] compute() throws InterruptedException, ExecutionException {
        if (n == 0) return new int[]{0, 0};
        
        int numProcessors = Runtime.getRuntime().availableProcessors();
        int chunkSize = Math.max(1, totalPerms / (numProcessors * 4));
        
        ExecutorService executor = Executors.newFixedThreadPool(numProcessors);
        List<Future<Result>> futures = new ArrayList<>();
        
        for (int start = 0; start < totalPerms; start += chunkSize) {
            final int finalStart = start;
            final int finalEnd = Math.min(start + chunkSize, totalPerms);
            
            futures.add(executor.submit(() -> processSlice(finalStart, finalEnd)));
        }
        
        int maxFlips = 0;
        int checksum = 0;
        
        for (Future<Result> future : futures) {
            Result result = future.get();
            if (result.maxFlips > maxFlips) {
                maxFlips = result.maxFlips;
            }
            checksum += result.checksum;
        }
        
        executor.shutdown();
        return new int[]{checksum, maxFlips};
    }
    
    public static void main(String[] args) throws Exception {
        int n = (args.length > 0) ? Integer.parseInt(args[0]) : 7;
        
        FannkuchRedux fannkuch = new FannkuchRedux(n);
        int[] result = fannkuch.compute();
        
        System.out.println(result[0]);
        System.out.println("Pfannkuchen(" + n + ") = " + result[1]);
    }
}
import java.util.*;

public class FannkuchRedux {
    
    public static int countFlips(int[] perm) {
        int count = 0;
        int first = perm[0];
        
        if (first == 0) return count;
        
        int[] current = perm.clone();
        
        while (current[0] != 0) {
            int k = current[0] + 1;
            // Reverse first k elements
            for (int i = 0; i < k / 2; i++) {
                int temp = current[i];
                current[i] = current[k - 1 - i];
                current[k - 1 - i] = temp;
            }
            count++;
        }
        
        return count;
    }
    
    public static int[] fannkuchRedux(int n) {
        int maxFlips = 0;
        int checksum = 0;
        
        // Generate initial permutation
        int[] perm = new int[n];
        for (int i = 0; i < n; i++) {
            perm[i] = i;
        }
        
        int index = 0;
        do {
            int flips = countFlips(perm);
            
            if (flips > maxFlips) {
                maxFlips = flips;
            }
            
            if (index % 2 == 0) {
                checksum += flips;
            } else {
                checksum -= flips;
            }
            
            index++;
        } while (nextPermutation(perm));
        
        return new int[]{maxFlips, checksum};
    }
    
    // Generate next permutation in lexicographic order
    private static boolean nextPermutation(int[] array) {
        // Find the largest index i such that array[i] < array[i + 1]
        int i = array.length - 2;
        while (i >= 0 && array[i] >= array[i + 1]) {
            i--;
        }
        
        if (i < 0) {
            return false;
        }
        
        // Find the largest index j such that array[i] < array[j]
        int j = array.length - 1;
        while (array[j] <= array[i]) {
            j--;
        }
        
        // Swap array[i] and array[j]
        int temp = array[i];
        array[i] = array[j];
        array[j] = temp;
        
        // Reverse the sequence from array[i + 1] to the end
        int left = i + 1;
        int right = array.length - 1;
        while (left < right) {
            temp = array[left];
            array[left] = array[right];
            array[right] = temp;
            left++;
            right--;
        }
        
        return true;
    }
    
    public static void main(String[] args) {
        int n = 7;
        int[] result = fannkuchRedux(n);
        System.out.println("Pfannkuchen(" + n + ") = " + result[0]);
        System.out.println("Checksum = " + result[1]);
    }
}
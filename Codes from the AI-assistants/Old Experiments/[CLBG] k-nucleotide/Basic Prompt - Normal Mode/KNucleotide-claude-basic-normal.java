import java.io.*;
import java.util.*;

/**
 * K-nucleotide frequency analysis implementation
 * Reads FASTA format from stdin and analyzes DNA sequence THREE
 */
public class KNucleotide {
    
    public static String readFastaSequenceThree(BufferedReader reader) throws IOException {
        Map<String, StringBuilder> sequences = new HashMap<>();
        String currentSeq = null;
        StringBuilder currentData = new StringBuilder();
        String line;
        
        while ((line = reader.readLine()) != null) {
            line = line.trim();
            if (line.startsWith(">")) {
                if (currentSeq != null) {
                    sequences.put(currentSeq, new StringBuilder(currentData.toString()));
                }
                currentSeq = line.substring(1); // Remove '>' prefix
                currentData = new StringBuilder();
            } else {
                currentData.append(line.toUpperCase());
            }
        }
        
        // Don't forget the last sequence
        if (currentSeq != null) {
            sequences.put(currentSeq, currentData);
        }
        
        // Extract sequence THREE
        for (Map.Entry<String, StringBuilder> entry : sequences.entrySet()) {
            if (entry.getKey().toUpperCase().contains("THREE")) {
                return entry.getValue().toString();
            }
        }
        
        // If no sequence named THREE found, return the longest sequence
        if (!sequences.isEmpty()) {
            return sequences.values().stream()
                .max(Comparator.comparing(sb -> sb.length()))
                .map(StringBuilder::toString)
                .orElse("");
        }
        
        return "";
    }
    
    /**
     * Update hash table with k-nucleotide counts for all reading frames
     */
    public static void updateHashTable(Map<String, Integer> hashTable, String dnaSequence, int k) {
        int seqLen = dnaSequence.length();
        
        // Process all possible k-nucleotides (all reading frames)
        for (int i = 0; i <= seqLen - k; i++) {
            String kNucleotide = dnaSequence.substring(i, i + k);
            hashTable.put(kNucleotide, hashTable.getOrDefault(kNucleotide, 0) + 1);
        }
    }
    
    public static void printFrequencyTable(Map<String, Integer> hashTable) {
        int totalCount = hashTable.values().stream().mapToInt(Integer::intValue).sum();
        if (totalCount == 0) return;
        
        List<Map.Entry<String, Integer>> entries = new ArrayList<>(hashTable.entrySet());
        
        // Sort by descending frequency, then ascending nucleotide key
        entries.sort((a, b) -> {
            double freqA = (a.getValue() * 100.0) / totalCount;
            double freqB = (b.getValue() * 100.0) / totalCount;
            int freqCompare = Double.compare(freqB, freqA); // Descending frequency
            if (freqCompare != 0) return freqCompare;
            return a.getKey().compareTo(b.getKey()); // Ascending key
        });
        
        for (Map.Entry<String, Integer> entry : entries) {
            double percentage = (entry.getValue() * 100.0) / totalCount;
            System.out.printf("%s %.3f%n", entry.getKey(), percentage);
        }
        System.out.println();
    }
    
    public static void printSpecificCounts(Map<String, Integer> hashTable, String[] targets) {
        for (String target : targets) {
            int count = hashTable.getOrDefault(target, 0);
            System.out.printf("%d\t%s%n", count, target);
        }
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        
        // Read DNA sequence THREE from stdin
        String dnaSequence = readFastaSequenceThree(reader);
        
        if (dnaSequence.isEmpty()) {
            System.err.println("No DNA sequence found");
            return;
        }
        
        // Hash tables for different k-nucleotide lengths
        Map<Integer, Map<String, Integer>> hashTables = new HashMap<>();
        
        // Count 1-nucleotide and 2-nucleotide sequences
        for (int k : new int[]{1, 2}) {
            hashTables.put(k, new HashMap<>());
            updateHashTable(hashTables.get(k), dnaSequence, k);
            printFrequencyTable(hashTables.get(k));
        }
        
        // Count 3, 4, 6, 12, and 18-nucleotide sequences for specific targets
        Map<Integer, String[]> targetSequences = new HashMap<>();
        targetSequences.put(3, new String[]{"GGT"});
        targetSequences.put(4, new String[]{"GGTA"});
        targetSequences.put(6, new String[]{"GGTATT"});
        targetSequences.put(12, new String[]{"GGTATTTTAATT"});
        targetSequences.put(18, new String[]{"GGTATTTTAATTTATAGT"});
        
        for (int k : new int[]{3, 4, 6, 12, 18}) {
            hashTables.put(k, new HashMap<>());
            updateHashTable(hashTables.get(k), dnaSequence, k);
            
            if (targetSequences.containsKey(k)) {
                printSpecificCounts(hashTables.get(k), targetSequences.get(k));
            }
        }
        
        reader.close();
    }
}
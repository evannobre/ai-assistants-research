import java.io.*;
import java.util.regex.*;

public class RegexRedux {
    
    public static void main(String[] args) throws IOException {
        // Read all input from stdin
        StringBuilder inputBuilder = new StringBuilder();
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(System.in)
        );
        
        String line;
        while ((line = reader.readLine()) != null) {
            inputBuilder.append(line).append('\n');
        }
        reader.close();
        
        String inputData = inputBuilder.toString();
        int initialLength = inputData.length();
        
        // Remove FASTA descriptions and linefeeds
        String sequence = inputData.replaceAll(">.*\n|\n", "");
        int cleanedLength = sequence.length();
        
        // Define the 8-mer patterns
        String[] patterns = {
            "agggtaaa|tttaccct",
            "[cgt]gggtaaa|tttaccc[acg]",
            "a[act]ggtaaa|tttacc[agt]t",
            "ag[act]gtaaa|tttac[agt]ct",
            "agg[act]taaa|ttta[agt]cct",
            "aggg[acg]aaa|ttt[cgt]ccct",
            "agggt[cgt]aa|tt[acg]accct",
            "agggta[cgt]a|t[acg]taccct",
            "agggtaa[cgt]|[acg]ttaccct"
        };
        
        // Count matches for each pattern
        for (String pattern : patterns) {
            Pattern p = Pattern.compile(pattern);
            Matcher m = p.matcher(sequence);
            int count = 0;
            while (m.find()) {
                count++;
            }
            System.out.println(pattern + " " + count);
        }
        
        // Define magic patterns and replacements
        String[][] replacements = {
            {"tHa[Nt]", "<4>"},
            {"aND|caN|Ha[DS]|WaS", "<3>"},
            {"a[NSt]|BY", "<2>"},
            {"<[^>]*>", "|"},
            {"\\|[^|][^|]*\\|", "-"}
        };
        
        // Apply replacements one at a time
        String resultSequence = sequence;
        for (String[] replacement : replacements) {
            resultSequence = resultSequence.replaceAll(
                replacement[0], 
                replacement[1]
            );
        }
        
        int finalLength = resultSequence.length();
        
        // Write the three recorded sequence lengths
        System.out.println();
        System.out.println(initialLength);
        System.out.println(cleanedLength);
        System.out.println(finalLength);
    }
}
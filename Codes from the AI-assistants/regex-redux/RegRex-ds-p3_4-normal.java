import java.io.*;
import java.util.Scanner;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class RegexRedux {
    public static void main(String[] args) throws IOException {
        // Read all input from stdin
        Scanner scanner = new Scanner(System.in);
        scanner.useDelimiter("\\A");
        String input = scanner.hasNext() ? scanner.next() : "";
        scanner.close();
        
        // Record initial length
        int initialLength = input.length();
        
        // 1. Remove FASTA sequence descriptions and linefeeds
        String cleaned = input.replaceAll(">.*\\n|\\n", "");
        int cleanedLength = cleaned.length();
        
        // 2. Count patterns
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
        
        for (String patternStr : patterns) {
            Pattern pattern = Pattern.compile(patternStr);
            Matcher matcher = pattern.matcher(cleaned);
            int count = 0;
            while (matcher.find()) {
                count++;
            }
            System.out.println(patternStr + " " + count);
        }
        
        // 3. Apply substitution patterns
        String[][] substitutions = {
            {"tHa[Nt]", "<4>"},
            {"aND|caN|Ha[DS]|WaS", "<3>"},
            {"a[NSt]|BY", "<2>"},
            {"<[^>]*>", "|"},
            {"\\\\|[^|][^|]*\\\\|", "-"}
        };
        
        String transformed = cleaned;
        for (String[] sub : substitutions) {
            transformed = transformed.replaceAll(sub[0], sub[1]);
        }
        
        // Record final length
        int finalLength = transformed.length();
        
        // 4. Print lengths
        System.out.println("\n" + initialLength);
        System.out.println(cleanedLength);
        System.out.println(finalLength);
    }
}
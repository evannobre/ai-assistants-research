import java.nio.file.*;
import java.io.IOException;

public class ReverseComplement {
    public static void main(String[] args) throws IOException {
        if (args.length != 1) {
            System.out.println("Usage: java ReverseComplement <dna_file>");
            return;
        }

        String dna = Files.readString(Path.of(args[0])).trim();
        StringBuilder out = new StringBuilder();

        for (int i = dna.length() - 1; i >= 0; i--) {
            char c = dna.charAt(i);
            switch (c) {
                case 'A': out.append('T'); break;
                case 'T': out.append('A'); break;
                case 'C': out.append('G'); break;
                case 'G': out.append('C'); break;
                case 'a': out.append('t'); break;
                case 't': out.append('a'); break;
                case 'c': out.append('g'); break;
                case 'g': out.append('c'); break;
                default:  out.append('N');
            }
        }

        System.out.println(out.toString());
    }
}

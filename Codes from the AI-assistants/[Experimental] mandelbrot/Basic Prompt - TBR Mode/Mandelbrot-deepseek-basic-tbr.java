import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

public class Mandelbrot {
    
    static class Complex {
        double real;
        double imag;
        
        Complex(double real, double imag) {
            this.real = real;
            this.imag = imag;
        }
        
        Complex square() {
            return new Complex(real * real - imag * imag, 2 * real * imag);
        }
        
        Complex add(Complex other) {
            return new Complex(real + other.real, imag + other.imag);
        }
        
        double magnitude() {
            return Math.sqrt(real * real + imag * imag);
        }
    }
    
    public static int mandelbrotIterations(Complex c, int maxIter) {
        Complex z = new Complex(0, 0);
        int iter = 0;
        
        while (z.magnitude() <= 2.0 && iter < maxIter) {
            z = z.square().add(c);
            iter++;
        }
        
        return iter;
    }
    
    public static void generateMandelbrotPBM(int N, int maxIter, String filename) {
        double xMin = -2.0, xMax = 1.0;
        double yMin = -1.5, yMax = 1.5;
        double xStep = (xMax - xMin) / (N - 1);
        double yStep = (yMax - yMin) / (N - 1);
        
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
            // Write PBM header
            writer.write("P1\n");
            writer.write(N + " " + N + "\n");
            
            for (int i = 0; i < N; i++) {
                StringBuilder row = new StringBuilder();
                for (int j = 0; j < N; j++) {
                    Complex c = new Complex(xMin + j * xStep, yMin + i * yStep);
                    int iter = mandelbrotIterations(c, maxIter);
                    
                    // 1 for in set (black), 0 for out of set (white)
                    int pixel = (iter == maxIter) ? 1 : 0;
                    row.append(pixel).append(" ");
                }
                writer.write(row.toString().trim());
                writer.newLine();
            }
            
            System.out.println("Mandelbrot set saved to " + filename);
            
        } catch (IOException e) {
            System.err.println("Error writing file: " + e.getMessage());
        }
    }
    
    public static void main(String[] args) {
        int N = 800;
        int maxIter = 1000;
        
        generateMandelbrotPBM(N, maxIter, "mandelbrot.pbm");
    }
}
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
        
        Complex add(Complex other) {
            return new Complex(this.real + other.real, this.imag + other.imag);
        }
        
        Complex multiply(Complex other) {
            double newReal = this.real * other.real - this.imag * other.imag;
            double newImag = this.real * other.imag + this.imag * other.real;
            return new Complex(newReal, newImag);
        }
        
        double magnitude() {
            return Math.sqrt(real * real + imag * imag);
        }
    }
    
    public static int mandelbrotIterations(Complex c, int maxIter) {
        Complex z = new Complex(0, 0);
        
        for (int i = 0; i < maxIter; i++) {
            if (z.magnitude() > 2.0) {
                return i;
            }
            z = z.multiply(z).add(c);
        }
        
        return maxIter;
    }
    
    public static void generateMandelbrotPBM(String filename, int width, int height,
                                           double xMin, double xMax, double yMin, double yMax,
                                           int maxIter) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
            // Write PBM header
            writer.write("P1");
            writer.newLine();
            writer.write(width + " " + height);
            writer.newLine();
            
            // Generate Mandelbrot data
            for (int y = 0; y < height; y++) {
                StringBuilder row = new StringBuilder();
                double im = yMin + (yMax - yMin) * y / (height - 1);
                
                for (int x = 0; x < width; x++) {
                    double re = xMin + (xMax - xMin) * x / (width - 1);
                    Complex c = new Complex(re, im);
                    
                    int iterCount = mandelbrotIterations(c, maxIter);
                    
                    // 1 for points in Mandelbrot set, 0 for points outside
                    int pixel = (iterCount == maxIter) ? 1 : 0;
                    row.append(pixel).append(" ");
                }
                writer.write(row.toString().trim());
                writer.newLine();
            }
        }
    }
    
    public static void main(String[] args) {
        int width = 800;
        int height = 600;
        int maxIter = 1000;
        
        // Define the region to plot
        double xMin = -2.0;
        double xMax = 1.0;
        double yMin = -1.0;
        double yMax = 1.0;
        
        try {
            generateMandelbrotPBM("mandelbrot.pbm", width, height,
                                 xMin, xMax, yMin, yMax, maxIter);
            System.out.println("Mandelbrot set saved to mandelbrot.pbm");
        } catch (IOException e) {
            System.err.println("Error writing file: " + e.getMessage());
        }
    }
}
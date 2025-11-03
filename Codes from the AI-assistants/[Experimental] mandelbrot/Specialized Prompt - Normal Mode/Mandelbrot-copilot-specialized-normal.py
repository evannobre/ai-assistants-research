import math

def mandelbrot(N, max_iter=1000, x_min=-2.0, x_max=1.0, y_min=-1.5, y_max=1.5, output_file="mandelbrot.pbm"):
    """
    Generate a Mandelbrot set and save it as a PBM (Portable Bitmap) file.
    """
    with open(output_file, "w") as f:
        f.write(f"P1\n{N} {N}\n")  # PBM header

        for j in range(N):
            y = y_min + (y_max - y_min) * j / (N - 1)
            row = []
            for i in range(N):
                x = x_min + (x_max - x_min) * i / (N - 1)
                c = complex(x, y)
                z = 0
                is_inside = True
                for _ in range(max_iter):
                    z = z * z + c
                    if abs(z) > 2:
                        is_inside = False
                        break
                row.append("1" if is_inside else "0")
            f.write(" ".join(row) + "\n")

if __name__ == "__main__":
    mandelbrot(N=1024)  # You can increase N up to 4096 depending on RAM
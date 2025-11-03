def mandelbrot(N, max_iter=1000):
    # Image header for PBM (ASCII)
    pbm = ["P1", f"{N} {N}"]

    for j in range(N):
        row = []
        for i in range(N):
            # Map pixel to complex plane
            x = (i / N) * 3.0 - 2.0       # [-2.0, 1.0]
            y = (j / N) * 3.0 - 1.5       # [-1.5, 1.5]
            c = complex(x, y)
            z = 0j

            # Iterate recurrence
            for n in range(max_iter):
                z = z*z + c
                if abs(z) > 2.0:
                    break

            # Mandelbrot set: black (0) if in set, white (1) if escaped
            row.append("0" if n == max_iter - 1 else "1")
        pbm.append(" ".join(row))

    return "\n".join(pbm)

# Save to file
with open("mandelbrot.pbm", "w") as f:
    f.write(mandelbrot(N=512))
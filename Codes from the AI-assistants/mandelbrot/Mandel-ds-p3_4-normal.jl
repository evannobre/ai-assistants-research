function mandelbrot(N::Int, max_iter::Int=1000)
    # Create complex grid
    x = range(-2.0, 1.0, length=N)
    y = range(-1.5, 1.5, length=N)
    
    # Initialize output matrix
    img = zeros(UInt8, N, N)
    
    @inbounds for j in 1:N, i in 1:N
        c = complex(x[i], y[j])
        z = complex(0.0, 0.0)
        k = 0
        
        while k < max_iter && abs2(z) ≤ 4.0
            z = z^2 + c
            k += 1
        end
        
        img[j, i] = k == max_iter ? 0x00 : UInt8(255 * k ÷ max_iter)
    end
    
    return img
end

function main()
    if length(ARGS) != 1
        println("Usage: julia $(basename(@__FILE__)) N")
        exit(1)
    end
    
    N = parse(Int, ARGS[1])
    max_iter = 1000
    
    start_time = time()
    
    # Generate image
    img = mandelbrot(N, max_iter)
    
    # Write PGM (P5 format)
    write(stdout, "P5\n$N $N\n255\n")
    write(stdout, img)
    
    elapsed = time() - start_time
    @error("Time: $(elapsed) seconds")
end

main()
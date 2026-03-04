#!/bin/bash
# pi_generator.sh

# Machin's formula using bc
generate_pi() {
    local digits=$1
    local scale=$((digits + 10))
    
    echo "scale=$scale; \
          4*(4*a(1/5) - a(1/239))" | bc -l | \
          head -c $((digits + 2))  # +2 for "3."
}

# Alternative: Spigot algorithm using bc
generate_pi_spigot() {
    local digits=$1
    local scale=$((digits + 10))
    
    echo "scale=$scale; \
          define pi(x) { \
              auto a, b, c, d, e, f, g, h, i; \
              a = 10000; \
              b = x; \
              c = x; \
              d = 0; \
              e = 0; \
              f = 0; \
              for (i = 0; i < x; i++) { \
                  c = (b - c) * (b - c); \
                  d = d + c; \
                  e = e + 1; \
              } \
              f = a * (b * b - d / e) / (b * b - d / e + c); \
              return(f); \
          } \
          pi($digits)" | bc -l
}

if [ $# -ne 1 ]; then
    echo "Usage: $0 <digits>"
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+$ ]] || [ "$1" -le 0 ]; then
    echo "Please provide a positive integer"
    exit 1
fi

echo "Generating $1 digits of Pi..."
generate_pi "$1"
echo
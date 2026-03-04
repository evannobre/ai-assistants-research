#!/usr/bin/env python3
"""
Test script to verify the Spigot algorithm implementations.
"""
import subprocess
import sys

def test_small_values():
    """Test with small number of digits."""
    test_cases = [
        (3, 10, "3141592653"),
        (3, 20, "31415926535897932384"),
        (4, 10, "3141592653"),
        (4, 20, "31415926535897932384"),
    ]
    
    for method, n_digits, expected in test_cases:
        print(f"\nTesting extract({method}) with {n_digits} digits...")
        
        # Run the spigot algorithm
        result = subprocess.run(
            [sys.executable, "spigot_pi.py", str(method), str(n_digits)],
            capture_output=True,
            text=True
        )
        
        # Extract digits from output
        lines = result.stdout.strip().split('\n')
        digits = []
        for line in lines:
            if line.strip():
                # Get the digit part (first 10 characters)
                digit_part = line[:10].strip()
                if digit_part:
                    digits.append(digit_part)
        
        actual = ''.join(digits)[:n_digits]
        
        if actual == expected:
            print(f"✓ extract({method}) correct for {n_digits} digits")
        else:
            print(f"✗ extract({method}) incorrect for {n_digits} digits")
            print(f"  Expected: {expected}")
            print(f"  Got:      {actual}")
            # Show first mismatch
            for i, (e, a) in enumerate(zip(expected, actual)):
                if e != a:
                    print(f"  First mismatch at position {i}: expected '{e}', got '{a}'")
                    break

def benchmark_performance():
    """Benchmark both methods with 10000 digits."""
    print("\n" + "="*60)
    print("Performance benchmark with 10000 digits")
    print("="*60)
    
    for method in [3, 4]:
        print(f"\nBenchmarking extract({method})...")
        
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "spigot_pi.py", str(method), "10000"],
            capture_output=True,
            text=True
        )
        elapsed = time.time() - start_time
        
        # Check if we got 10000 digits
        lines = result.stdout.strip().split('\n')
        total_digits = 0
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        total_digits = int(parts[1])
                    except ValueError:
                        pass
        
        print(f"Time: {elapsed:.2f} seconds")
        print(f"Digits calculated: {total_digits}")
        print(f"Digits per second: {total_digits/elapsed:.0f}")

if __name__ == "__main__":
    import time
    
    print("Testing Spigot π Algorithm Implementations")
    print("="*60)
    
    # Test with small values first
    test_small_values()
    
    # Then benchmark
    benchmark_performance()
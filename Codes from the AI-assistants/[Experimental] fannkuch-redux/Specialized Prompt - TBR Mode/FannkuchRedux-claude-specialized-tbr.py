#!/usr/bin/env python3
"""
Fannkuch-Redux Benchmark Implementation

This module implements the fannkuch-redux algorithm, which generates all
permutations of integers from 1 to n and counts the maximum number of
'pancake flips' required to sort each permutation.

Memory: O(n) - operates on permutations in-place
Time: O(n! * n) - must process all permutations

Author: Computer Science Specialist
Date: 2025
"""

from typing import List, Tuple
import sys


def count_flips(perm: List[int]) -> int:
    """
    Count the number of flips required to sort a permutation.
    
    A flip operation reverses the first k elements, where k is the value
    at the first position. Continue until the first element is 1.
    
    Args:
        perm: A list representing a permutation (modified in-place)
    
    Returns:
        The number of flips performed
    """
    flips = 0
    first = perm[0]
    
    while first != 0:  # Using 0-indexed (0 represents 1)
        # Reverse the first 'first+1' elements
        perm[:first + 1] = perm[:first + 1][::-1]
        flips += 1
        first = perm[0]
    
    return flips


def fannkuch_redux(n: int) -> Tuple[int, int]:
    """
    Solve the fannkuch-redux problem for a given n.
    
    Generates all permutations of integers 0 to n-1 (representing 1 to n)
    and calculates:
    - Maximum flip count across all permutations
    - Checksum (alternating sum of flip counts)
    
    Args:
        n: The size of the permutation (must be > 0)
    
    Returns:
        A tuple (checksum, max_flips)
    
    Raises:
        ValueError: If n is less than 1
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    
    # Initialize permutation array (0-indexed for efficiency)
    perm = list(range(n))
    perm1 = list(range(n))
    count = list(range(n, 0, -1))
    
    max_flips = 0
    checksum = 0
    perm_count = 0
    sign = 1
    
    while True:
        # Calculate flips for current permutation
        if perm[0] != 0:
            # Copy current permutation for flip counting
            perm1[:] = perm
            flips = count_flips(perm1)
            
            max_flips = max(max_flips, flips)
            checksum += sign * flips
        
        sign = -sign
        perm_count += 1
        
        # Generate next permutation using Heap's algorithm variant
        # This is optimized for fannkuch (based on CLBG implementations)
        k = 0
        while k < n:
            if count[k] > 1:
                count[k] -= 1
                
                # Rotate the first k+2 elements
                if k % 2 == 0:
                    perm[0], perm[1] = perm[1], perm[0]
                else:
                    perm[0], perm[k + 1] = perm[k + 1], perm[0]
                break
            else:
                count[k] = k + 2
                
                # Rotate left the first k+2 elements
                temp = perm[0]
                for i in range(k + 1):
                    perm[i] = perm[i + 1]
                perm[k + 1] = temp
                
                k += 1
        else:
            # All permutations generated
            break
    
    return checksum, max_flips


def main() -> None:
    """
    Main entry point for the fannkuch-redux program.
    
    Reads n from command line arguments or prompts user for input.
    Prints the checksum and maximum flip count (Pfannkuchen).
    """
    try:
        if len(sys.argv) > 1:
            n = int(sys.argv[1])
        else:
            n = int(input("Enter n: "))
        
        if n < 1:
            print("Error: n must be at least 1", file=sys.stderr)
            sys.exit(1)
        
        if n > 12:
            print(f"Warning: n={n} will take significant time and memory", 
                  file=sys.stderr)
        
        checksum, max_flips = fannkuch_redux(n)
        
        print(f"{checksum}")
        print(f"Pfannkuchen({n}) = {max_flips}")
        
    except ValueError as e:
        print(f"Error: Invalid input - {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
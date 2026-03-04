#!/usr/bin/env python3
"""Test script for reverse complement processor"""

import subprocess
import tempfile
import os
import sys

def create_test_files():
    """Create test DNA files"""
    
    # Test DNA sequences
    fasta_content = """>seq1
ATCGATCGATCG
>seq2
GCTAGCTAGCTA
"""
    
    fastq_content = """@read1
ATCGATCGATCG
+
IIIIIIIIIIII
@read2
GCTAGCTAGCTA
+
IIIIIIIIIIII
"""
    
    # Create test files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
        f.write(fasta_content)
        fasta_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fastq', delete=False) as f:
        f.write(fastq_content)
        fastq_file = f.name
    
    return fasta_file, fastq_file

def test_basic_functionality():
    """Test basic reverse complement functionality"""
    print("Testing basic functionality...")
    
    # Create a small test file
    test_dna = "ATCG" * 1000
    expected = "CGAT" * 1000
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_dna)
        test_file = f.name
    
    try:
        # Run the script
        output_file = test_file.replace('.txt', '_output.txt')
        cmd = [sys.executable, 'reverse_complement.py', test_file, '-o', output_file, '--no-stats']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        
        # Read output
        with open(output_file, 'r') as f:
            output = f.read().strip()
        
        # Verify
        if output == expected:
            print("✓ Basic test passed")
            return True
        else:
            print(f"✗ Basic test failed. Got {output[:20]}..., expected {expected[:20]}...")
            return False
            
    finally:
        # Cleanup
        for f in [test_file, output_file]:
            if os.path.exists(f):
                os.remove(f)

def test_large_file():
    """Test with a larger file"""
    print("\nTesting with larger file...")
    
    # Create a 10MB DNA file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dna', delete=False) as f:
        # Write 10MB of DNA data
        chunk = "ATCG" * 250  # 1000 bases
        for _ in range(10000):  # 10,000 chunks = ~10MB
            f.write(chunk)
        large_file = f.name
    
    try:
        # Run with chunking
        cmd = [
            sys.executable, 'reverse_complement.py',
            large_file,
            '--chunk-size', '1048576',
            '--workers', '2',
            '--no-stats'
        ]
        
        import time
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - start
        
        if result.returncode == 0:
            print(f"✓ Large file test passed in {elapsed:.2f} seconds")
            return True
        else:
            print(f"✗ Large file test failed: {result.stderr}")
            return False
            
    finally:
        if os.path.exists(large_file):
            os.remove(large_file)
        output_file = large_file.replace('.dna', '_reverse_complement.dna')
        if os.path.exists(output_file):
            os.remove(output_file)

def test_formats():
    """Test different file formats"""
    print("\nTesting file formats...")
    
    fasta_file, fastq_file = create_test_files()
    
    try:
        # Test FASTA
        cmd = [sys.executable, 'reverse_complement.py', fasta_file, '--no-stats']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ FASTA test failed: {result.stderr}")
            return False
        
        # Test FASTQ
        cmd = [sys.executable, 'reverse_complement.py', fastq_file, '--no-stats']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ File formats test passed")
            return True
        else:
            print(f"✗ FASTQ test failed: {result.stderr}")
            return False
            
    finally:
        for f in [fasta_file, fastq_file]:
            if os.path.exists(f):
                os.remove(f)
            output_file = f.replace('.fasta', '_reverse_complement.fasta').replace('.fastq', '_reverse_complement.fastq')
            if os.path.exists(output_file):
                os.remove(output_file)

if __name__ == "__main__":
    print("=" * 60)
    print("Reverse Complement Processor Test Suite")
    print("=" * 60)
    
    tests = [
        test_basic_functionality,
        test_formats,
        test_large_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    sys.exit(0 if passed == total else 1)
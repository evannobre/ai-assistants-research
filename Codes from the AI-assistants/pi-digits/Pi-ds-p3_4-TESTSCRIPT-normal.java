import subprocess
import time

def test_performance():
    """Test both implementations with 10000 digits"""
    print("Testing performance with 10000 digits...")
    print("=" * 50)
    
    # Test extract(3)
    print("\nTesting extract(3) implementation:")
    start = time.time()
    result = subprocess.run(["python", "pi_spigot.py", "10000"], 
                          capture_output=True, text=True)
    end = time.time()
    print(f"Time: {end - start:.2f} seconds")
    
    # Test extract(4)
    print("\n\nTesting extract(4) implementation:")
    start = time.time()
    result = subprocess.run(["python", "pi_spigot_v2.py", "10000"], 
                          capture_output=True, text=True)
    end = time.time()
    print(f"Time: {end - start:.2f} seconds")

if __name__ == "__main__":
    test_performance()
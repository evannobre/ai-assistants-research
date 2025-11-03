def A(i, j):
  """Calculates A(i, j) using 1-based indexing."""
  i_j = i + j - 2
  return 1.0 / (i_j * (i_j + 1) // 2 + i)

import numpy as np

def Av(v):
  """Computes the matrix-vector product A*v."""
  n = len(v)
  w = np.zeros(n)
  for i in range(n):
    # The inner loop computes the dot product of the i-th row of A with v
    w[i] = sum(A(i + 1, j + 1) * v[j] for j in range(n))
  return w

import numpy as np

def Atv(v):
  """Computes the transposed matrix-vector product Aᵗ*v."""
  n = len(v)
  u = np.zeros(n)
  for i in range(n):
    # The inner loop computes the dot product of the i-th column of A with v
    u[i] = sum(A(j + 1, i + 1) * v[j] for j in range(n))
  return u

def AtAv(v):
  """Computes Aᵗ * (A * v) by composing the two functions."""
  return Atv(Av(v))

import sys
import numpy as np

# ... (include the four function definitions from above) ...

def main():
  """
  Main program to calculate the spectral norm.
  Expects a command-line argument for the vector size.
  """
  try:
    # 1. Get vector size n from command line
    n = int(sys.argv[1])
  except (IndexError, ValueError):
    print("Usage: python spectral_norm.py <n>")
    sys.exit(1)

  # 2. Initialize vectors
  u = np.ones(n, dtype=np.float64)
  v = np.zeros(n, dtype=np.float64)

  # 3. Perform 10 iterations of the Power Method
  for _ in range(10):
    v = AtAv(u)
    u = AtAv(v)

  # 4. Calculate the result
  # The dot product u•v is u.dot(v) or np.dot(u, v)
  v_dot_v = np.dot(v, v)
  u_dot_v = np.dot(u, v)

  result = np.sqrt(u_dot_v / v_dot_v)

  # Expected result is ~1.27422415
  print(f"{result:.9f}")

if __name__ == "__main__":
  main()
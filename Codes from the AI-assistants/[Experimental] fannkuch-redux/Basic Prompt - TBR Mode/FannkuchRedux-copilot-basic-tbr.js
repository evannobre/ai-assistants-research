// Node.js implementation with in-place next permutation (lexicographic)
function nextPermutation(arr) {
  // find pivot
  let i = arr.length - 2;
  while (i >= 0 && arr[i] >= arr[i + 1]) i--;
  if (i < 0) return false;
  let j = arr.length - 1;
  while (arr[j] <= arr[i]) j--;
  [arr[i], arr[j]] = [arr[j], arr[i]];
  // reverse suffix
  let a = i + 1, b = arr.length - 1;
  while (a < b) {
    [arr[a], arr[b]] = [arr[b], arr[a]];
    a++; b--;
  }
  return true;
}

function fannkuchRedux(n) {
  const p = Array.from({length: n}, (_, i) => i);
  let maxFlips = 0;
  let checksum = 0;
  let idx = 0;
  while (true) {
    // copy to working array for flips
    const q = p.slice();
    let flips = 0;
    while (q[0] !== 0) {
      const k = q[0] + 1;
      // reverse prefix k
      for (let i = 0, j = k - 1; i < j; i++, j--) {
        const t = q[i]; q[i] = q[j]; q[j] = t;
      }
      flips++;
    }
    if (flips > maxFlips) maxFlips = flips;
    checksum += (idx % 2 === 0) ? flips : -flips;
    idx++;
    if (!nextPermutation(p)) break;
  }
  return { checksum, maxFlips };
}

// Example run
const n = parseInt(process.argv[2] || "7", 10);
const result = fannkuchRedux(n);
console.log(result.checksum);
console.log(`Pfannkuchen(${n}) = ${result.maxFlips}`);
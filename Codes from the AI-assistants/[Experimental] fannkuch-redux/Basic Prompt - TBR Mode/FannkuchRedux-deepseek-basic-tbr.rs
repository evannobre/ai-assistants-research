fn count_flips(perm: &[i32]) -> i32 {
    let mut count = 0;
    let first = perm[0];
    
    if first == 0 {
        return count;
    }
    
    let mut current = perm.to_vec();
    
    while current[0] != 0 {
        let k = current[0] as usize + 1;
        // Reverse first k elements
        current[0..k].reverse();
        count += 1;
    }
    
    count
}

fn fannkuch_redux(n: i32) -> (i32, i32) {
    let mut max_flips = 0;
    let mut checksum = 0;
    
    let mut perm: Vec<i32> = (0..n).collect();
    let mut index = 0;
    
    // Heap's algorithm for permutation generation
    let mut c = vec![0; n as usize];
    let mut i = 0;
    
    while i < n as usize {
        if c[i] < i {
            if i % 2 == 0 {
                perm.swap(0, i);
            } else {
                perm.swap(c[i], i);
            }
            
            let flips = count_flips(&perm);
            
            if flips > max_flips {
                max_flips = flips;
            }
            
            if index % 2 == 0 {
                checksum += flips;
            } else {
                checksum -= flips;
            }
            
            index += 1;
            
            c[i] += 1;
            i = 0;
        } else {
            c[i] = 0;
            i += 1;
        }
    }
    
    (max_flips, checksum)
}

fn main() {
    let n = 7;
    let (max_flips, checksum) = fannkuch_redux(n);
    println!("Pfannkuchen({}) = {}", n, max_flips);
    println!("Checksum = {}", checksum);
}
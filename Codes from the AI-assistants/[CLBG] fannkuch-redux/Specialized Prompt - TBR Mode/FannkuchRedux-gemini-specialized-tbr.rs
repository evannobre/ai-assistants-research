// main.rs
use std::env;
use std::thread;
use std::cmp::max;

fn fannkuch(n: usize) -> (i32, i32) {
    let num_threads = thread::available_parallelism().map_or(1, |n| n.get());
    let fact_n = (1..=n).product::<usize>();
    let chunk_size = (fact_n + num_threads - 1) / num_threads;

    let mut threads = vec![];

    for i in 0..num_threads {
        let start_idx = i * chunk_size;
        let end_idx = (start_idx + chunk_size).min(fact_n);

        threads.push(thread::spawn(move || {
            let mut p = vec![0; n];
            let mut pp = vec![0; n];
            let mut count = vec![0; n];

            let mut max_flips = 0;
            let mut checksum = 0;
            let mut perm_count = 0;

            // Initialize first permutation for this chunk
            let mut temp_idx = start_idx;
            for i in (0..n).rev() {
                let d = temp_idx / (1..=i).product::<usize>();
                temp_idx %= (1..=i).product::<usize>();
                count[i] = d;

                for j in 0..=i {
                    pp[j] = j;
                }
                for j in 0..=d {
                    p[j] = pp.remove(d - j);
                }
                for j in 0..=(i - d - 1) {
                    p[d + 1 + j] = pp[j];
                }
            }

            // Main loop for the chunk
            loop {
                // Flip logic
                let mut k = p[0];
                if k != 0 {
                    let mut flips = 0;
                    let mut p_temp = p.clone();
                    while k != 0 {
                        p_temp[..=k].reverse();
                        flips += 1;
                        k = p_temp[0];
                    }
                    max_flips = max(max_flips, flips);
                    if perm_count % 2 == 0 {
                        checksum += flips;
                    } else {
                        checksum -= flips;
                    }
                }

                perm_count += 1;
                if perm_count >= end_idx - start_idx {
                    break;
                }

                // Generate next permutation (Plain Changes)
                let mut i = 1;
                loop {
                    if i >= n {
                        return (max_flips, checksum);
                    }
                    let temp = p[0];
                    for j in 0..i {
                        p[j] = p[j + 1];
                    }
                    p[i] = temp;
                    count[i] += 1;
                    if count[i] <= i {
                        break;
                    }
                    count[i] = 0;
                    i += 1;
                }
            }
            (max_flips, checksum)
        }));
    }

    let mut total_checksum = 0;
    let mut max_flips_total = 0;

    for handle in threads {
        let (thread_max_flips, thread_checksum) = handle.join().unwrap();
        total_checksum += thread_checksum;
        max_flips_total = max(max_flips_total, thread_max_flips);
    }

    (max_flips_total, total_checksum)
}


fn main() {
    let n: usize = env::args()
        .nth(1)
        .expect("Please provide a number n.")
        .parse()
        .expect("Argument must be a number.");

    // The problem statement uses 1-based indexing, so we adjust.
    // Our arrays are 0-indexed (0 to n-1), representing numbers 1 to n.
    let (max_flips, checksum) = fannkuch(n);

    // Final result output as per problem specification.
    println!("{}", checksum);
    println!("Pfannkuchen({}) = {}", n, max_flips);
}
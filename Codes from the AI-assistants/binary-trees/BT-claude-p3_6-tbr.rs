/**
 * Binary Trees Benchmark - Rust Implementation
 * Allocates and deallocates many binary trees using Rust's ownership system.
 * 
 * Build: rustc -O binarytrees.rs -o binarytrees_rust
 * Or: cargo build --release
 * Run: ./binarytrees_rust <max_depth>
 * Example: ./binarytrees_rust 21
 */

use std::env;

/// Binary tree node with left and right children.
/// Interior nodes and leaf nodes use the same allocation.
/// Box provides heap allocation and automatic cleanup via RAII.
struct TreeNode {
    left: Option<Box<TreeNode>>,
    right: Option<Box<TreeNode>>,
}

impl TreeNode {
    /// Create a new tree node with optional children.
    fn new(left: Option<Box<TreeNode>>, right: Option<Box<TreeNode>>) -> TreeNode {
        TreeNode { left, right }
    }
}

/// Create a binary tree of given depth.
/// Uses Box for heap allocation, which is automatically freed when dropped.
fn make_tree(depth: i32) -> Box<TreeNode> {
    if depth > 0 {
        Box::new(TreeNode::new(
            Some(make_tree(depth - 1)),
            Some(make_tree(depth - 1)),
        ))
    } else {
        Box::new(TreeNode::new(None, None))
    }
}

/// Count nodes in the tree (walk the tree).
/// Returns the total number of nodes.
fn check_tree(node: &TreeNode) -> i32 {
    match (&node.left, &node.right) {
        (None, None) => 1,
        (Some(l), Some(r)) => 1 + check_tree(l) + check_tree(r),
        _ => unreachable!(), // Trees are always perfect binary trees
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        eprintln!("Usage: {} <max_depth>", args[0]);
        eprintln!("Example: {} 21", args[0]);
        std::process::exit(1);
    }
    
    let max_depth: i32 = args[1].parse().expect("Invalid depth argument");
    let min_depth: i32 = 4;
    
    let stretch_depth = max_depth + 1;
    
    // Stretch memory - allocate and check a large tree, then let it be dropped
    {
        let stretch_tree = make_tree(stretch_depth);
        println!(
            "stretch tree of depth {}\t check: {}",
            stretch_depth,
            check_tree(&stretch_tree)
        );
        // stretch_tree is automatically freed here when it goes out of scope
    }
    
    // Allocate long-lived tree that will survive while other trees are created/destroyed
    let long_lived_tree = make_tree(max_depth);
    
    // Allocate, walk, and deallocate many bottom-up binary trees
    let mut depth = min_depth;
    while depth <= max_depth {
        let iterations = 1 << (max_depth - depth + min_depth);
        let mut check_sum = 0;
        
        for _ in 0..iterations {
            // Allocate tree
            let temp_tree = make_tree(depth);
            // Walk tree and count nodes
            check_sum += check_tree(&temp_tree);
            // Tree automatically freed when it goes out of scope
        }
        
        println!(
            "{}\t trees of depth {}\t check: {}",
            iterations, depth, check_sum
        );
        depth += 2;
    }
    
    // Check that long-lived tree still exists
    println!(
        "long lived tree of depth {}\t check: {}",
        max_depth,
        check_tree(&long_lived_tree)
    );
    // long_lived_tree is automatically freed here
}

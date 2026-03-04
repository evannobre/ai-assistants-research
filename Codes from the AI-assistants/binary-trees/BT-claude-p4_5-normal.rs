use std::env;

// Tree node struct - same for leaf and interior nodes
struct Node {
    left: Option<Box<Node>>,
    right: Option<Box<Node>>,
}

impl Node {
    fn new(left: Option<Box<Node>>, right: Option<Box<Node>>) -> Self {
        Node { left, right }
    }
}

// Create a tree of given depth
fn create_tree(depth: i32) -> Box<Node> {
    if depth == 0 {
        Box::new(Node::new(None, None))
    } else {
        Box::new(Node::new(
            Some(create_tree(depth - 1)),
            Some(create_tree(depth - 1)),
        ))
    }
}

// Check tree exists by counting nodes
fn check_tree(node: &Node) -> i32 {
    match (&node.left, &node.right) {
        (None, None) => 1,
        (Some(left), Some(right)) => 1 + check_tree(left) + check_tree(right),
        _ => unreachable!(),
    }
}

fn main() {
    let n = env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(10);
    
    let min_depth = 4;
    let max_depth = if min_depth + 2 > n { min_depth + 2 } else { n };
    let stretch_depth = max_depth + 1;
    
    // Stretch memory - allocate and deallocate
    {
        let stretch_tree = create_tree(stretch_depth);
        println!(
            "stretch tree of depth {}\t check: {}",
            stretch_depth,
            check_tree(&stretch_tree)
        );
    }
    
    // Allocate long-lived tree
    let long_lived_tree = create_tree(max_depth);
    
    // Allocate, walk, and deallocate many bottom-up trees
    for depth in (min_depth..=max_depth).step_by(2) {
        let iterations = 1 << (max_depth - depth + min_depth);
        let mut check = 0;
        
        for _ in 0..iterations {
            let tree = create_tree(depth);
            check += check_tree(&tree);
        }
        
        println!("{}\t trees of depth {}\t check: {}", iterations, depth, check);
    }
    
    // Check long-lived tree still exists
    println!(
        "long lived tree of depth {}\t check: {}",
        max_depth,
        check_tree(&long_lived_tree)
    );
}

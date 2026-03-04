use std::env;

struct TreeNode {
    left: Option<Box<TreeNode>>,
    right: Option<Box<TreeNode>>,
}

impl TreeNode {
    fn new(depth: i32) -> Box<TreeNode> {
        if depth > 0 {
            Box::new(TreeNode {
                left: Some(TreeNode::new(depth - 1)),
                right: Some(TreeNode::new(depth - 1)),
            })
        } else {
            Box::new(TreeNode {
                left: None,
                right: None,
            })
        }
    }

    fn check(&self) -> i32 {
        match (&self.left, &self.right) {
            (None, None) => 1,
            (Some(l), Some(r)) => 1 + l.check() + r.check(),
            _ => unreachable!(),
        }
    }
}

fn main() {
    let n = env::args()
        .nth(1)
        .and_then(|arg| arg.parse().ok())
        .unwrap_or(10);

    let min_depth = 4;
    let max_depth = if min_depth + 2 > n { min_depth + 2 } else { n };
    let stretch_depth = max_depth + 1;

    // Stretch memory
    {
        let stretch_tree = TreeNode::new(stretch_depth);
        println!(
            "stretch tree of depth {}\t check: {}",
            stretch_depth,
            stretch_tree.check()
        );
    }

    // Create long-lived tree
    let long_lived_tree = TreeNode::new(max_depth);

    // Allocate, walk, and deallocate many bottom-up trees
    for depth in (min_depth..=max_depth).step_by(2) {
        let iterations = 1 << (max_depth - depth + min_depth);
        let mut check = 0;

        for _ in 0..iterations {
            let tree = TreeNode::new(depth);
            check += tree.check();
        }

        println!("{}\t trees of depth {}\t check: {}", iterations, depth, check);
    }

    // Check long-lived tree
    println!(
        "long lived tree of depth {}\t check: {}",
        max_depth,
        long_lived_tree.check()
    );
}

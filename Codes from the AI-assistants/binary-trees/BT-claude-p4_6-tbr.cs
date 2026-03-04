using System;

public class BinaryTrees
{
    private class TreeNode
    {
        public TreeNode left;
        public TreeNode right;

        public TreeNode(int depth)
        {
            if (depth > 0)
            {
                left = new TreeNode(depth - 1);
                right = new TreeNode(depth - 1);
            }
        }

        public int Check()
        {
            if (left == null)
            {
                return 1;
            }
            return 1 + left.Check() + right.Check();
        }
    }

    public static void Main(string[] args)
    {
        int n = args.Length > 0 ? int.Parse(args[0]) : 10;

        const int minDepth = 4;
        int maxDepth = Math.Max(minDepth + 2, n);
        int stretchDepth = maxDepth + 1;

        // Stretch memory
        {
            TreeNode stretchTree = new TreeNode(stretchDepth);
            Console.WriteLine($"stretch tree of depth {stretchDepth}\t check: {stretchTree.Check()}");
        }

        // Create long-lived tree
        TreeNode longLivedTree = new TreeNode(maxDepth);

        // Allocate, walk, and deallocate many bottom-up trees
        for (int depth = minDepth; depth <= maxDepth; depth += 2)
        {
            int iterations = 1 << (maxDepth - depth + minDepth);
            int check = 0;

            for (int i = 0; i < iterations; i++)
            {
                TreeNode tree = new TreeNode(depth);
                check += tree.Check();
            }

            Console.WriteLine($"{iterations}\t trees of depth {depth}\t check: {check}");
        }

        // Check long-lived tree
        Console.WriteLine($"long lived tree of depth {maxDepth}\t check: {longLivedTree.Check()}");
    }
}

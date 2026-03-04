using System;

public class BinaryTrees
{
    // Tree node class - same for leaf and interior nodes
    class Node
    {
        public Node left;
        public Node right;
        
        public Node(Node left = null, Node right = null)
        {
            this.left = left;
            this.right = right;
        }
    }
    
    // Create a tree of given depth
    static Node CreateTree(int depth)
    {
        if (depth == 0)
        {
            return new Node();
        }
        return new Node(CreateTree(depth - 1), CreateTree(depth - 1));
    }
    
    // Check tree exists by counting nodes
    static int CheckTree(Node node)
    {
        if (node.left == null)
        {
            return 1;
        }
        return 1 + CheckTree(node.left) + CheckTree(node.right);
    }
    
    public static void Main(string[] args)
    {
        int n = args.Length > 0 ? int.Parse(args[0]) : 10;
        int minDepth = 4;
        int maxDepth = Math.Max(minDepth + 2, n);
        int stretchDepth = maxDepth + 1;
        
        // Stretch memory - allocate and deallocate
        {
            Node stretchTree = CreateTree(stretchDepth);
            Console.WriteLine($"stretch tree of depth {stretchDepth}\t check: {CheckTree(stretchTree)}");
        }
        
        // Allocate long-lived tree
        Node longLivedTree = CreateTree(maxDepth);
        
        // Allocate, walk, and deallocate many bottom-up trees
        for (int depth = minDepth; depth <= maxDepth; depth += 2)
        {
            int iterations = 1 << (maxDepth - depth + minDepth);
            int check = 0;
            
            for (int i = 1; i <= iterations; i++)
            {
                Node tree = CreateTree(depth);
                check += CheckTree(tree);
            }
            
            Console.WriteLine($"{iterations}\t trees of depth {depth}\t check: {check}");
        }
        
        // Check long-lived tree still exists
        Console.WriteLine($"long lived tree of depth {maxDepth}\t check: {CheckTree(longLivedTree)}");
    }
}

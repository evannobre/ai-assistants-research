using System;
using System.Collections.Generic;

class TreeNode
{
    public int Value { get; set; }
    public int Level { get; set; }
    public TreeNode Left { get; set; }
    public TreeNode Right { get; set; }
    
    public TreeNode(int value, int level)
    {
        Value = value;
        Level = level;
        Left = null;
        Right = null;
    }
}

class BinaryTreeBuilder
{
    private static int nodeCounter = 0;
    
    public static TreeNode BuildPerfectTree(int depth)
    {
        if (depth < 0) return null;
        
        nodeCounter = 0;
        TreeNode root = new TreeNode(nodeCounter++, 0);
        
        // Use .NET Queue<T> (native collection)
        Queue<TreeNode> nodeQueue = new Queue<TreeNode>();
        nodeQueue.Enqueue(root);
        
        while (nodeQueue.Count > 0)
        {
            TreeNode current = nodeQueue.Dequeue();
            
            if (current.Level < depth)
            {
                // Allocate left child
                current.Left = new TreeNode(nodeCounter++, current.Level + 1);
                nodeQueue.Enqueue(current.Left);
                
                // Allocate right child
                current.Right = new TreeNode(nodeCounter++, current.Level + 1);
                nodeQueue.Enqueue(current.Right);
            }
        }
        
        return root;
    }
    
    public static void PrintTreeStats(int depth)
    {
        int expectedNodes = (int)Math.Pow(2, depth + 1) - 1;
        Console.WriteLine("Tree Statistics:");
        Console.WriteLine($"Depth: {depth}");
        Console.WriteLine($"Total Nodes Allocated: {nodeCounter}");
        Console.WriteLine($"Expected Nodes: {expectedNodes}");
    }
    
    static void Main(string[] args)
    {
        int depth = 10;
        
        Console.WriteLine($"Building perfect binary tree of depth {depth}...");
        TreeNode root = BuildPerfectTree(depth);
        
        PrintTreeStats(depth);
        
        // Monitor memory before GC
        long memoryBefore = GC.GetTotalMemory(false);
        Console.WriteLine($"\nMemory before GC: {memoryBefore:N0} bytes");
        
        Console.WriteLine("\nTree built successfully. Root reference held (no GC yet).");
        
        // Force GC to demonstrate collection
        root = null;
        GC.Collect();
        GC.WaitForPendingFinalizers();
        
        long memoryAfter = GC.GetTotalMemory(true);
        Console.WriteLine($"\nMemory after GC: {memoryAfter:N0} bytes");
        Console.WriteLine($"Memory freed: {memoryBefore - memoryAfter:N0} bytes");
    }
}
class Node {
    int value;
    Node left;
    Node right;

    Node(int value) {
        this.value = value;
    }
}

public class PerfectTreeBuilder {

    public static Node buildPerfectTree(int depth) {
        if (depth < 0) return null;

        int totalNodes = (1 << (depth + 1)) - 1;

        // 1. Allocate array of nodes
        Node[] nodes = new Node[totalNodes];

        // 2. Initialize nodes
        for (int i = 0; i < totalNodes; i++) {
            nodes[i] = new Node(i);
        }

        // 3. Link children
        for (int i = 0; i < totalNodes; i++) {
            int leftIndex  = 2 * i + 1;
            int rightIndex = 2 * i + 2;

            if (leftIndex < totalNodes) {
                nodes[i].left = nodes[leftIndex];
            }
            if (rightIndex < totalNodes) {
                nodes[i].right = nodes[rightIndex];
            }
        }

        // 4. Root is at index 0
        return nodes[0];
    }
}

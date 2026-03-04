class Node { Node left, right; int value; }
public static Node buildPerfect(int N) {
    int total = (1 << (N+1)) - 1; // 2^(N+1)-1
    Node[] nodes = new Node[total];
    for (int i = 0; i < total; i++) nodes[i] = new Node();
    for (int i = 0; i < total; i++) {
        int l = 2*i + 1, r = 2*i + 2;
        if (l < total) nodes[i].left = nodes[l];
        if (r < total) nodes[i].right = nodes[r];
    }
    // keep 'nodes' referenced in scope to prevent GC
    return nodes[0];
}

type Node struct { Left, Right *Node }
func BuildPerfect(N int) *Node {
    total := (1 << (N+1)) - 1
    nodes := make([]*Node, total)
    for i := 0; i < total; i++ { nodes[i] = &Node{} }
    for i := 0; i < total; i++ {
        l, r := 2*i+1, 2*i+2
        if l < total { nodes[i].Left = nodes[l] }
        if r < total { nodes[i].Right = nodes[r] }
    }
    return nodes[0] // keep 'nodes' in scope or as package var to prevent GC
}

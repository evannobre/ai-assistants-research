#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct Node {
    struct Node *left;
    struct Node *right;
} Node;

typedef struct Arena {
    Node *buf;
    size_t cap;
    size_t used;
} Arena;

static inline size_t nodes_for_depth(int depth) {
    // perfect tree nodes = 2^(depth+1) - 1
    return ((size_t)1 << (depth + 1)) - 1;
}

static Arena arena_create(size_t cap) {
    Arena a;
    a.buf = (Node *)malloc(cap * sizeof(Node));
    if (!a.buf) {
        fprintf(stderr, "malloc failed\n");
        exit(1);
    }
    a.cap = cap;
    a.used = 0;
    return a;
}

static inline void arena_reset(Arena *a) {
    a->used = 0;
}

static void arena_destroy(Arena *a) {
    free(a->buf);
    a->buf = NULL;
    a->cap = 0;
    a->used = 0;
}

static inline Node *arena_alloc_node(Arena *a) {
    // No GC: nodes live until arena_reset/destroy.
    if (a->used >= a->cap) {
        fprintf(stderr, "arena exhausted\n");
        exit(1);
    }
    return &a->buf[a->used++];
}

static Node *make_tree(Arena *a, int depth) {
    Node *n = arena_alloc_node(a);
    if (depth <= 0) {
        n->left = NULL;
        n->right = NULL;
    } else {
        n->left  = make_tree(a, depth - 1);
        n->right = make_tree(a, depth - 1);
    }
    return n;
}

static int check_tree(const Node *n) {
    // checksum: count nodes (1 + left + right)
    if (!n->left) return 1;
    return 1 + check_tree(n->left) + check_tree(n->right);
}

int main(int argc, char **argv) {
    int N = (argc > 1) ? atoi(argv[1]) : 10;

    const int minDepth = 4;
    int maxDepth = (N > minDepth + 2) ? N : (minDepth + 2);
    int stretchDepth = maxDepth + 1;

    // 1) Stretch tree
    {
        Arena a = arena_create(nodes_for_depth(stretchDepth));
        Node *t = make_tree(&a, stretchDepth);
        int c = check_tree(t);
        printf("stretch tree of depth %d\t check: %d\n", stretchDepth, c);
        arena_destroy(&a);
    }

    // 2) Long-lived tree
    Arena longArena = arena_create(nodes_for_depth(maxDepth));
    Node *longLived = make_tree(&longArena, maxDepth);

    // 3) Many temporary trees
    for (int d = minDepth; d <= maxDepth; d += 2) {
        int iterations = 1 << (maxDepth - d + minDepth);
        int chk = 0;

        // Reuse one arena buffer for all trees at this depth:
        Arena tmp = arena_create(nodes_for_depth(d));

        for (int i = 0; i < iterations; i++) {
            arena_reset(&tmp);
            Node *t = make_tree(&tmp, d);
            chk += check_tree(t);
        }

        printf("%d\t trees of depth %d\t check: %d\n", iterations, d, chk);
        arena_destroy(&tmp);
    }

    // 4) Long-lived tree check, then free
    {
        int c = check_tree(longLived);
        printf("long lived tree of depth %d\t check: %d\n", maxDepth, c);
        arena_destroy(&longArena);
    }

    return 0;
}

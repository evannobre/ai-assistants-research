// binary_trees_arena.c
// Perfect binary trees with explicit memory allocation via bump arena (node pool).
// Build: gcc -O3 -march=native -DNDEBUG binary_trees_arena.c -o binary_trees

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct Node {
    struct Node* left;
    struct Node* right;
    int32_t item;
} Node;

typedef struct Arena {
    Node*  buf;
    size_t cap;
    size_t idx;
} Arena;

static inline size_t nodes_for_depth(int depth) {
    // Perfect binary tree: 2^(depth+1) - 1 nodes
    // Use size_t / 64-bit shifts; depth should be "reasonable" (benchmark typically <= ~21-24).
    return ((size_t)1u << (depth + 1)) - 1u;
}

static Arena arena_create(size_t cap) {
    Arena a;
    a.cap = cap;
    a.idx = 0;
    a.buf = (Node*)malloc(cap * sizeof(Node));
    if (!a.buf) {
        fprintf(stderr, "Out of memory allocating %zu nodes\n", cap);
        exit(1);
    }
    return a;
}

static inline void arena_reset(Arena* a) {
    a->idx = 0;
}

static inline void arena_destroy(Arena* a) {
    free(a->buf);
    a->buf = NULL;
    a->cap = 0;
    a->idx = 0;
}

static inline Node* arena_alloc_node(Arena* a) {
    // No bounds checks in hot path beyond a single branch.
    if (a->idx >= a->cap) {
        fprintf(stderr, "Arena overflow: idx=%zu cap=%zu\n", a->idx, a->cap);
        exit(1);
    }
    return &a->buf[a->idx++];
}

static Node* make_tree(Arena* a, int32_t item, int depth) {
    Node* n = arena_alloc_node(a);
    n->item = item;

    if (depth <= 0) {
        n->left  = NULL;
        n->right = NULL;
        return n;
    }

    // Benchmark-style item propagation:
    // left:  item*2 - 1
    // right: item*2
    n->left  = make_tree(a, item * 2 - 1, depth - 1);
    n->right = make_tree(a, item * 2,     depth - 1);
    return n;
}

static int32_t check_tree(const Node* n) {
    // Classic benchmark checksum:
    // item + check(left) - check(right)
    if (!n->left) return n->item;
    return n->item + check_tree(n->left) - check_tree(n->right);
}

static int max_int(int a, int b) { return a > b ? a : b; }

int main(int argc, char** argv) {
    int N = (argc > 1) ? atoi(argv[1]) : 10;

    const int minDepth = 4;
    const int maxDepth = max_int(minDepth + 2, N);
    const int stretchDepth = maxDepth + 1;

    // 1) Stretch tree (short-lived)
    {
        Arena stretch = arena_create(nodes_for_depth(stretchDepth));
        Node* t = make_tree(&stretch, 0, stretchDepth);
        int32_t chk = check_tree(t);
        printf("stretch tree of depth %d\t check: %d\n", stretchDepth, chk);
        arena_destroy(&stretch);
    }

    // 2) Long-lived tree
    Arena longLived = arena_create(nodes_for_depth(maxDepth));
    Node* longTree = make_tree(&longLived, 0, maxDepth);

    // 3) Many temporary trees (reuse one arena per depth)
    for (int depth = minDepth; depth <= maxDepth; depth += 2) {
        // iterations = 2^(maxDepth - depth + minDepth)
        const int iters = 1 << (maxDepth - depth + minDepth);

        Arena tmp = arena_create(nodes_for_depth(depth));
        int32_t chk = 0;

        for (int i = 1; i <= iters; i++) {
            arena_reset(&tmp);
            chk += check_tree(make_tree(&tmp, (int32_t)i, depth));

            arena_reset(&tmp);
            chk += check_tree(make_tree(&tmp, (int32_t)(-i), depth));
        }

        printf("%d\t trees of depth %d\t check: %d\n", iters * 2, depth, chk);
        arena_destroy(&tmp);
    }

    // 4) Long-lived check (kept alive until now)
    printf("long lived tree of depth %d\t check: %d\n", maxDepth, check_tree(longTree));
    arena_destroy(&longLived);

    return 0;
}

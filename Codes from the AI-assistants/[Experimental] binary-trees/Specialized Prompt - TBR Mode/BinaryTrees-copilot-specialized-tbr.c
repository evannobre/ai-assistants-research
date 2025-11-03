#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <sys/mman.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <math.h>

/* Node layout: only two pointers, no payload */
typedef struct Node {
    struct Node *left;
    struct Node *right;
} Node;

/* Safety fraction of total RAM to use */
#define RAM_SAFETY_FRACTION 0.75

/* Compute 2^(exp) safely. Returns 0 on overflow. */
static int64_t pow2_checked(int exp) {
    if (exp < 0 || exp >= 63) return 0;
    return (int64_t)1 << exp;
}

/* Compute number of nodes for perfect tree of height H: 2^(H+1)-1.
   Return 0 on overflow or invalid H. */
static uint64_t nodes_for_height(int height) {
    if (height < 0) return 0;
    int shift = height + 1;
    if (shift >= 63) return 0;
    uint64_t v = ((uint64_t)1 << shift) - 1ULL;
    return v;
}

/* Get total physical RAM bytes (sysconf) */
static uint64_t get_physical_ram_bytes() {
    long pages = sysconf(_SC_PHYS_PAGES);
    long page_size = sysconf(_SC_PAGESIZE);
    if (pages <= 0 || page_size <= 0) return 0;
    return (uint64_t)pages * (uint64_t)page_size;
}

/* Allocate a contiguous pool via mmap */
static Node *allocate_node_pool_mmap(uint64_t node_count) {
    size_t node_size = sizeof(Node);
    uint64_t total = node_count * (uint64_t)node_size;
    if (total == 0) return NULL;

    void *p = mmap(NULL, total, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS | MAP_POPULATE, -1, 0);
    if (p == MAP_FAILED) {
        return NULL;
    }
    /* Zero-initialized by MAP_ANONYMOUS + MAP_POPULATE on most systems, but ensure */
    memset(p, 0, total);
    return (Node *)p;
}

/* Free mmap pool */
static void free_node_pool_mmap(Node *pool, uint64_t node_count) {
    if (!pool) return;
    size_t total = node_count * sizeof(Node);
    munmap((void *)pool, total);
}

/* Build perfect tree in the contiguous pool.
   Indexing: nodes in array at indices 0..N-1 where root=0.
   For node i: left = 2*i+1, right = 2*i+2 if those indices < N. */
static Node *build_perfect_tree_in_pool(Node *pool, uint64_t node_count) {
    if (!pool || node_count == 0) return NULL;
    for (uint64_t i = 0; i < node_count; ++i) {
        uint64_t li = 2*i + 1;
        uint64_t ri = 2*i + 2;
        pool[i].left = (li < node_count) ? &pool[li] : NULL;
        pool[i].right = (ri < node_count) ? &pool[ri] : NULL;
    }
    return &pool[0];
}

/* Simple level-order traversal to verify structure and count nodes (iterative) */
static uint64_t count_nodes_level_order(Node *root) {
    if (!root) return 0;
    /* For a perfect tree we know exact count, but we traverse to verify pointers. */
    /* We'll use a simple dynamic circular buffer queue allocated on heap. */
    size_t cap = 1024;
    Node **q = malloc(cap * sizeof(Node *));
    if (!q) return 0;
    size_t head = 0, tail = 0;
    auto enqueue = [&](Node *n) {
        if ((tail + 1) % cap == head) {
            size_t newcap = cap * 2;
            Node **newq = realloc(q, newcap * sizeof(Node *));
            if (!newq) return -1;
            /* adjust circular buffer if needed */
            if (head > tail) {
                memmove(&newq[cap], &newq[0], tail * sizeof(Node *));
                tail += cap;
            }
            q = newq;
            cap = newcap;
        }
        q[tail] = n;
        tail = (tail + 1) % cap;
        return 0;
    };
    uint64_t count = 0;
    /* enqueue root */
    q[tail++] = root;
    while (head != tail) {
        Node *n = q[head++];
        if (head == cap) head = 0;
        ++count;
        if (n->left) {
            if (enqueue(n->left) < 0) break;
        }
        if (n->right) {
            if (enqueue(n->right) < 0) break;
        }
    }
    free(q);
    return count;
}

/* Safe print of bytes in human readable form */
static void print_human_bytes(uint64_t bytes) {
    const char *units[] = {"B","KB","MB","GB","TB"};
    double v = (double)bytes;
    int u = 0;
    while (v >= 1024.0 && u < 4) { v /= 1024.0; ++u; }
    printf("%.3g %s", v, units[u]);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <height>\nCreate perfect balanced binary tree of given height (root height 0)\n", argv[0]);
        return 1;
    }
    char *end;
    long height = strtol(argv[1], &end, 10);
    if (*end != '\0' || height < 0 || height > 52) { /* guard against insane heights */
        fprintf(stderr, "Invalid height. Provide integer 0..52 (practical limit)\n");
        return 1;
    }

    uint64_t node_count = nodes_for_height((int)height);
    if (node_count == 0) {
        fprintf(stderr, "Requested height too large or invalid\n");
        return 1;
    }

    size_t node_size = sizeof(Node);
    __uint128_t total_bytes_128 = (__uint128_t)node_count * node_size;
    if (total_bytes_128 > (__uint128_t)UINT64_MAX) {
        fprintf(stderr, "Requested allocation overflows 64-bit size\n");
        return 1;
    }
    uint64_t total_bytes = (uint64_t)total_bytes_128;

    uint64_t phys_ram = get_physical_ram_bytes();
    if (phys_ram == 0) {
        fprintf(stderr, "Warning: cannot determine physical RAM; proceeding with allocation checks\n");
    }
    uint64_t allowed = (uint64_t)((long double)phys_ram * RAM_SAFETY_FRACTION);

    printf("Height: %ld; Nodes: %" PRIu64 "; Node size: %zu bytes; Total bytes: ", height, node_count, node_size);
    print_human_bytes(total_bytes);
    printf("\nPhysical RAM: ");
    print_human_bytes(phys_ram);
    printf(" ; Safety limit: ");
    print_human_bytes(allowed);
    printf("\n");

    if (phys_ram != 0 && total_bytes > allowed) {
        fprintf(stderr, "Refusing allocation: requested pool exceeds safety fraction of RAM\n");
        return 2;
    }

    Node *pool = allocate_node_pool_mmap(node_count);
    if (!pool) {
        fprintf(stderr, "mmap allocation failed: %s\n", strerror(errno));
        return 3;
    }

    Node *root = build_perfect_tree_in_pool(pool, node_count);
    if (!root) {
        fprintf(stderr, "Failed to build tree\n");
        free_node_pool_mmap(pool, node_count);
        return 4;
    }

    printf("Tree built. Verifying via iterative level-order traversal...\n");
    uint64_t counted = count_nodes_level_order(root);
    printf("Counted nodes by traversal: %" PRIu64 "\n", counted);
    if (counted != node_count) {
        fprintf(stderr, "Verification failed: expected %" PRIu64 " nodes but counted %" PRIu64 "\n", node_count, counted);
        free_node_pool_mmap(pool, node_count);
        return 5;
    }

    printf("Verification succeeded. Cleaning up.\n");
    free_node_pool_mmap(pool, node_count);
    printf("Done.\n");
    return 0;
}
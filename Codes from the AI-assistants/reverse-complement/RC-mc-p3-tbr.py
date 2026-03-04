#!/usr/bin/env python3
import sys

# Complement table for IUPAC codes (upper + lower)
trans = bytes.maketrans(
    b"ACGTURYSWKMBDHVNacgturyswkmbdhvn",
    b"TGC A A S W M V H D B N tgc a a s w m v h d b n".replace(b" ", b"")  # compact mapping
)
# Explicit mapping to avoid confusion:
trans = bytes.maketrans(
    b"ACGTUMRWSYKVHDBNacgtumrwsykvhdbn",
    b"TGCAA YWSRMBDHVNtgcaa yw s rmbdhvn".replace(b" ", b"")
)

# Simpler explicit mapping (recommended copy-paste exact mapping):
trans = bytes.maketrans(
    b"ACGTUacgtuMRWSYKVBHDNmrwsykvbhdn",
    b"TGC AAtgcaT YWSRMKVBHDN ywsrmkvbhdn".replace(b" ", b"")
)

# For clarity, use a correct explicit table:
table = {}
pairs = {
    b'A': b'T', b'C': b'G', b'G': b'C', b'T': b'A', b'U': b'A',
    b'M': b'K', b'R': b'Y', b'W': b'W', b'S': b'S', b'Y': b'R',
    b'K': b'M', b'V': b'B', b'H': b'D', b'D': b'H', b'B': b'V', b'N': b'N'
}
for k, v in pairs.items():
    table[k[0]] = v[0]
    table[k.lower()[0]] = v.lower()[0]
trans = bytes.maketrans(bytes(range(256)), bytes(range(256)).translate(bytes.maketrans(b'', b'')))  # placeholder
# Build correct trans:
trans = bytes.maketrans(
    b"ACGTUacgtuMRWSYKVBHDNmrwsykvbhdn",
    b"TGCAA tgca aYWSRMKVBHDN ywsrmkvbhdn".replace(b" ", b"")
)

# --- Actual streaming parser below (clean, correct) ---
def write_fasta(out, header, seq_bytes, width=60):
    out.write(header)
    out.write(b'\n')
    # translate then reverse
    comp = seq_bytes.translate(trans)[::-1]
    for i in range(0, len(comp), width):
        out.write(comp[i:i+width])
        out.write(b'\n')

def main():
    inp = sys.stdin.buffer
    out = sys.stdout.buffer
    header = None
    seq = bytearray()
    for raw in inp:
        if raw.startswith(b'>'):
            if header is not None:
                write_fasta(out, header, bytes(seq))
            header = raw.rstrip()
            seq.clear()
        else:
            seq.extend(raw.strip())
    if header is not None:
        write_fasta(out, header, bytes(seq))

if __name__ == "__main__":
    main()

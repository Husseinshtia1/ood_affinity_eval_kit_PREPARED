#!/usr/bin/env python3
import argparse, sys
def read_fasta(path):
    seqs = {}
    with open(path, 'r') as f:
        sid = None; buf = []
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith('>'):
                if sid is not None:
                    seqs[sid] = ''.join(buf).upper()
                sid = line[1:].split()[0]
                buf = []
            else:
                buf.append(line)
        if sid is not None:
            seqs[sid] = ''.join(buf).upper()
    return seqs
def nw_identity(a, b, match=1, mismatch=-1, gap=-1):
    n, m = len(a), len(b)
    S = [[0]*(m+1) for _ in range(n+1)]
    for i in range(1, n+1): S[i][0] = S[i-1][0] + gap
    for j in range(1, m+1): S[0][j] = S[0][j-1] + gap
    for i in range(1, n+1):
        ai = a[i-1]
        for j in range(1, m+1):
            s_diag = S[i-1][j-1] + (match if ai == b[j-1] else mismatch)
            s_up   = S[i-1][j] + gap
            s_left = S[i][j-1] + gap
            S[i][j] = max(s_diag, s_up, s_left)
    i, j = n, m; matches = 0; length = 0
    while i>0 or j>0:
        if i>0 and j>0 and S[i][j] == S[i-1][j-1] + (match if a[i-1]==b[j-1] else mismatch):
            length += 1
            if a[i-1]==b[j-1]: matches += 1
            i -= 1; j -= 1
        elif i>0 and S[i][j] == S[i-1][j] + gap:
            length += 1; i -= 1
        else:
            length += 1; j -= 1
    return 0.0 if length==0 else matches/length
def main():
    ap = argparse.ArgumentParser(description="Compute minimal global identity (NW) for test FASTA vs training FASTA.")
    ap.add_argument("--test_fasta", required=True)
    ap.add_argument("--train_fasta", required=True)
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--max_train", type=int, default=200)
    args = ap.parse_args()
    test = read_fasta(args.test_fasta)
    train = read_fasta(args.train_fasta)
    train_items = list(train.items())
    if len(train_items) > args.max_train:
        print(f"[warn] training set large; truncating to first {args.max_train}. Use MMseqs2 for scale.", file=sys.stderr)
        train_items = train_items[:args.max_train]
    with open(args.out_csv, "w") as out:
        out.write("protein_fasta_id,min_global_identity\n")
        for tid, tseq in test.items():
            best = 1.0
            for sid, sseq in train_items:
                ident = nw_identity(tseq, sseq)
                if ident < best: best = ident
            out.write(f"{tid},{best:.4f}\n")
    print(f"Wrote {args.out_csv}")
if __name__ == "__main__": main()

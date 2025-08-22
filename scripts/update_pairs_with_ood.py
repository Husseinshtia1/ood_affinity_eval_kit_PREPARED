#!/usr/bin/env python3
import argparse, csv
def load_map(path, key, val):
    d = {}
    with open(path, newline='') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            k = r.get(key,"").strip(); v = r.get(val,"").strip()
            if k: d[k] = v
    return d
def tf(x):
    try: return float(x)
    except: return None
def main():
    ap = argparse.ArgumentParser(description="Merge identity/tanimoto minima into pairs.csv and mark OOD flags.")
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--prot_csv", required=False)
    ap.add_argument("--lig_csv", required=False)
    ap.add_argument("--prot_thr", type=float, default=0.5)
    ap.add_argument("--lig_thr", type=float, default=0.30)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    prot_map = load_map(args.prot_csv, "protein_fasta_id", "min_global_identity") if args.prot_csv else {}
    lig_map  = load_map(args.lig_csv, "ligand_smiles_id", "min_ecfp4_tanimoto") if args.lig_csv else {}
    rows = []
    with open(args.pairs, newline='') as f:
        rdr = csv.DictReader(row for row in f if not row.startswith('#'))
        for r in rdr:
            pid = r.get("protein_fasta_id","").strip()
            lid = r.get("ligand_smiles_id","").strip()
            if pid and pid in prot_map:
                r["prot_identity_min_to_train"] = prot_map[pid]
            if lid and lid in lig_map:
                r["lig_tanimoto_min_to_train"] = lig_map[lid]
            pidv = tf(r.get("prot_identity_min_to_train",""))
            lidv = tf(r.get("lig_tanimoto_min_to_train",""))
            pood = (pidv is not None) and (pidv < args.prot_thr)
            lood = (lidv is not None) and (lidv <= args.lig_thr)
            r["ood_one_side"] = "1" if (pood or lood) else "0"
            r["ood_double"]   = "1" if (pood and lood) else "0"
            rows.append(r)
    outp = args.out or args.pairs.replace(".csv","_with_ood.csv")
    with open(outp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {outp}")
if __name__ == "__main__": main()

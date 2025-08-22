#!/usr/bin/env python3
import argparse, csv, sys
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, DataStructs
except Exception as e:
    Chem = None
def read_smiles_csv(path, id_col="ligand_smiles_id", smi_col="smiles"):
    rows = []
    with open(path, newline='') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rid = r.get(id_col,"").strip()
            smi = r.get(smi_col,"").strip()
            if rid and smi:
                rows.append((rid, smi))
    return rows
def fp(smi):
    m = Chem.MolFromSmiles(smi)
    if m is None: return None
    return AllChem.GetMorganFingerprintAsBitVect(m, radius=2, nBits=2048)
def main():
    ap = argparse.ArgumentParser(description="Compute minimal ECFP4 Tanimoto for test ligands vs training ligands.")
    ap.add_argument("--test_smiles_csv", required=True)
    ap.add_argument("--train_smiles_csv", required=True)
    ap.add_argument("--out_csv", required=True)
    args = ap.parse_args()
    if Chem is None:
        print("[error] RDKit is required. Install via conda: `conda install -c rdkit rdkit` or Linux: `pip install rdkit-pypi`")
        sys.exit(2)
    test = read_smiles_csv(args.test_smiles_csv)
    train = read_smiles_csv(args.train_smiles_csv)
    train_fps = []
    for tid, smi in train:
        mfp = fp(smi)
        if mfp is not None:
            train_fps.append((tid, mfp))
    with open(args.out_csv, "w", newline="") as out:
        w = csv.writer(out); w.writerow(["ligand_smiles_id","min_ecfp4_tanimoto"])
        for qid, smi in test:
            qf = fp(smi)
            if qf is None:
                w.writerow([qid, ""])
                continue
            best = 0.0
            for tid, tf in train_fps:
                sim = DataStructs.TanimotoSimilarity(qf, tf)
                if sim > best: best = sim
            w.writerow([qid, f"{best:.4f}"])
    print(f"Wrote {args.out_csv}")
if __name__ == "__main__": main()

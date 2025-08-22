#!/usr/bin/env bash
set -e
echo "[1/5] Proteins OOD distances"
python3 scripts/compute_protein_identity.py --test_fasta round1/test_proteins.fasta --train_fasta round1/train_proteins.fasta --out_csv round1/min_identity.csv
echo "[2/5] Ligands OOD distances (optional)"
python3 scripts/compute_ligand_tanimoto.py --test_smiles_csv round1/test_ligands.csv --train_smiles_csv round1/train_ligands.csv --out_csv round1/min_tanimoto.csv || echo "RDKit not installed; skipping ligands"
echo "[3/5] Merge OOD"
python3 scripts/update_pairs_with_ood.py --pairs round1/pairs.csv --prot_csv round1/min_identity.csv --lig_csv round1/min_tanimoto.csv --out round1/pairs_with_ood.csv || python3 scripts/update_pairs_with_ood.py --pairs round1/pairs.csv --prot_csv round1/min_identity.csv --out round1/pairs_with_ood.csv
echo "[4/5] Validate"
python3 scripts/validate_ood.py --pairs round1/pairs_with_ood.csv --threshold_id 0.5 --threshold_tan 0.30
echo "[5/5] Evaluate sample predictions"
python3 scripts/eval.py --truth round1/ground_truth.csv --pred predictions.csv --pairs round1/pairs_with_ood.csv --out round1/report_round1.json
echo "Done. See round1/report_round1.json"

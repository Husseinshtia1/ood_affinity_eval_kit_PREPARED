PY=python3
ROUND=round1

sanitize:
	$(PY) scripts/sanitize_predictions.py --pred predictions.csv

validate:
	$(PY) scripts/validate_ood.py --pairs $(ROUND)/pairs_with_ood.csv --threshold_id 0.5 --threshold_tan 0.30

eval:
	$(PY) scripts/eval.py --truth $(ROUND)/ground_truth.csv --pred predictions.csv --pairs $(ROUND)/pairs_with_ood.csv --out report.json

leaderboard:
	$(PY) scripts/leaderboard.py --truth $(ROUND)/ground_truth.csv --pairs $(ROUND)/pairs_with_ood.csv --subs submissions --out leaderboard.md

round1-ood-proteins:
	$(PY) scripts/compute_protein_identity.py --test_fasta $(ROUND)/test_proteins.fasta --train_fasta $(ROUND)/train_proteins.fasta --out_csv $(ROUND)/min_identity.csv

round1-ood-ligands:
	$(PY) scripts/compute_ligand_tanimoto.py --test_smiles_csv $(ROUND)/test_ligands.csv --train_smiles_csv $(ROUND)/train_ligands.csv --out_csv $(ROUND)/min_tanimoto.csv

round1-merge-ood:
	$(PY) scripts/update_pairs_with_ood.py --pairs $(ROUND)/pairs.csv --prot_csv $(ROUND)/min_identity.csv --lig_csv $(ROUND)/min_tanimoto.csv --out $(ROUND)/pairs_with_ood.csv

round1-validate:
	$(PY) scripts/validate_ood.py --pairs $(ROUND)/pairs_with_ood.csv --threshold_id 0.5 --threshold_tan 0.30

round1-eval:
	$(PY) scripts/eval.py --truth $(ROUND)/ground_truth.csv --pred predictions.csv --pairs $(ROUND)/pairs_with_ood.csv --out $(ROUND)/report_round1.json

round1-leaderboard:
	$(PY) scripts/leaderboard.py --truth $(ROUND)/ground_truth.csv --pairs $(ROUND)/pairs_with_ood.csv --subs submissions --out $(ROUND)/leaderboard_round1.md

hash-training:
	$(PY) scripts/hash_training_set.py --file training_ids.txt

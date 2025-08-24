
```markdown
# OOD Binding Affinity Evaluation Kit — PREPARED

Turn claims about **out-of-distribution (OOD)** binding-affinity prediction into **reproducible evidence**.

> **Round 1 Goal:** Predict log10(pK) for **Protein–Ligand (P–L)** or **Protein–Protein (P–P)** pairs on **OOD** data with:
>
> - **RMSE ≤ 0.30 log10(pK)**, and  
> - **Coverage ≥ 80%** within **±0.30 log10** (≈ factor of 2)

OOD is **numeric**, not subjective:
- **Protein OOD:** global sequence identity **< 50%** vs any training protein  
- **Ligand OOD:** ECFP4 Tanimoto **≤ 0.30** vs any training ligand

**Repo:** `https://github.com/Husseinshtia1/ood_affinity_eval_kit_PREPARED`

---

## Why this repo?

- **Explicit OOD** with measurable distances (identity, Tanimoto)  
- **Pass/Fail** acceptance tied to practical decision thresholds  
- **Bootstrap CIs** for metrics (RMSE/MAE/Pearson/Kendall/coverage)  
- **Leakage prevention** (`training_set_hash`) and distance audits  
- **Deterministic pipeline**: scripts + Makefile + CI → same inputs, same outputs

We don’t ship a “model”. We ship a **method** to test any model fairly.

---

## What’s inside

```

scripts/
compute\_protein\_identity.py      # minimal global identity (NW fallback)
compute\_ligand\_tanimoto.py       # minimal ECFP4 Tanimoto (requires RDKit)
update\_pairs\_with\_ood.py         # merge distances + set OOD flags
validate\_ood.py                  # check OOD flags and report counts
eval.py                          # RMSE/MAE/r/τ/coverage + bootstrap CIs
sanitize\_predictions.py          # schema & quality checks for predictions
leaderboard.py                   # rank multiple submissions
hash\_training\_set.py             # sha256 for training-set IDs
distance\_audit\_stub.py           # quick OOD audit summary

round1/
pairs.csv
ground\_truth.csv
test\_proteins.fasta
train\_proteins.fasta
test\_ligands.csv
train\_ligands.csv

Makefile
quickstart.sh
.github/workflows/eval\_round1.yml

````

---

## Install

Python ≥ 3.9 recommended. For the **ligand** OOD step you’ll need RDKit.

```bash
# (optional but recommended) conda
# conda create -n oodkit python=3.11 -y
# conda activate oodkit
# conda install -c rdkit rdkit
````

---

## Quick start

Use the included data to verify the pipeline runs end-to-end:

```bash
# 1) OOD distances
make round1-ood-proteins
make round1-ood-ligands   # optional; needs RDKit

# 2) Merge distances & validate OOD flags
make round1-merge-ood
make round1-validate

# 3) Evaluate (after labels are frozen)
make round1-eval

# 4) Leaderboard (for multiple CSVs under submissions/)
make round1-leaderboard
```

Or run everything with:

```bash
bash quickstart.sh
```

Outputs:

* `round1/pairs_with_ood.csv` (with distance columns + OOD flags)
* `round1/report_round1.json` (metrics + bootstrap CIs)
* `round1/leaderboard_round1.md/.csv` (if you have multiple submissions)

---

## File formats

**`round1/pairs.csv`** (publishable now; distance columns will be filled by scripts)

```csv
id,track,protein_fasta_id,ligand_smiles_id,protein2_fasta_id,info,assay_type
ex1,P-L,P12345,L_SMILES_001,,S1,SPR
ex2,P-P,P12345,,P67890,S1,SPR
```

**`round1/ground_truth.csv`** (freeze, then reveal after submissions)

```csv
id,pK,assay_type
ex1,7.25,SPR
ex2,6.90,SPR
```

**`predictions.csv`** (one per model/run)

```csv
id,y_pred_pK,track,info,model_name,training_set_hash
ex1,7.10,P-L,S1,YourModel,abcdef1234...
ex2,6.85,P-P,S1,YourModel,abcdef1234...
```

* `track` ∈ {`P-L`, `P-P`}
* `info` ∈ {`S1`,`S2`,`S3`} (free to use for scenario tags)
* `training_set_hash`: sha256 of a newline-sorted list of training IDs (see `hash_training_set.py`)

---

## OOD distances

* **Protein**: `compute_protein_identity.py` computes minimal **global identity** (Needleman–Wunsch fallback).
  For large scale, compute with **MMseqs2/BLAST** externally and import the CSV; then run `update_pairs_with_ood.py`.

* **Ligand**: `compute_ligand_tanimoto.py` computes minimal **ECFP4 Tanimoto** (needs RDKit).

`update_pairs_with_ood.py` merges distances into `pairs.csv` and sets:

* `prot_identity_min_to_train`
* `lig_tanimoto_min_to_train`
* `ood_one_side` / `ood_double`

> Default OOD thresholds: **protein identity < 0.50**, **ligand Tanimoto ≤ 0.30**.

---

## Acceptance & metrics

* **Pass** if:

  * `RMSE ≤ 0.30 log10(pK)` **and**
  * `Coverage ≥ 80%` within `±0.30`

* Reported:

  * `RMSE`, `MAE`, **Pearson r**, **Kendall τ**, and **coverage (±0.30)**
  * **Bootstrap CIs** for all metrics

`eval.py` writes a machine-readable `report_round1.json`.

---

## Leakage control

* Every submission includes `training_set_hash` (sha256 over training IDs).
* We publish **distance audits** (min identity / min Tanimoto) and OOD flags.
* This binds the OOD definition to the submitter’s *actual* training set and discourages leakage.

---

## CI

`.github/workflows/eval_round1.yml` provides a light GitHub Action to:

* sanity-check `predictions.csv`
* validate OOD flags
* run the evaluator and print `report_round1.json`


---

## Reproducibility

* Deterministic scripts/Make targets: **same inputs → same outputs**
* JSON reports and leaderboards can be committed and diffed across runs
* Bootstrap seeds are fixed by default (configurable in `eval.py`)

---

## Troubleshooting

* **RDKit missing** → ligand step fails. Install RDKit via conda or skip that step.
* **No overlapping IDs** → ensure `id` values match between `ground_truth.csv` and `predictions.csv`.
* **CSV comments** → lines starting with `#` are ignored; keep CSVs tidy.
* **Large protein sets** → prefer MMseqs2/BLAST for distances, then import CSV.

---

## Roadmap

* Round 2 (PPIs) with kinetic metrics (kon/koff) when standardized data are available
* Reliability diagrams & ECE for OOD calibration
* Docker/Conda environment for one-shot setup
* Assay Data Cards (protocol metadata) for stronger harmonization

---

## How to cite

> Shtiai, H. (2025). **OOD Binding Affinity Evaluation Kit — PREPARED** (Round 1).
> GitHub: `Husseinshtia1/ood_affinity_eval_kit_PREPARED`.


---

## License

 license file (MIT/Apache-2.0 recommended) at the repo root.

---


::contentReference[oaicite:0]{index=0}
```

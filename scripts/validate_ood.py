#!/usr/bin/env python3
import argparse, csv, sys
def clean_reader(fp):
    return csv.DictReader(row for row in fp if (not row.startswith('#') and row.strip()))
ap=argparse.ArgumentParser()
ap.add_argument("--pairs", required=True)
ap.add_argument("--threshold_id", type=float, default=0.5)
ap.add_argument("--threshold_tan", type=float, default=0.30)
a=ap.parse_args()
rows=list(clean_reader(open(a.pairs)))
if not rows: sys.exit("pairs csv empty or invalid")
one=dbl=0; n=len(rows)
def tf(x):
  try: return float(x)
  except: return None
for r in rows:
  pid=tf(r.get("prot_identity_min_to_train")); tan=tf(r.get("lig_tanimoto_min_to_train"))
  pood=pid is not None and pid<a.threshold_id
  lood=tan is not None and tan<=a.threshold_tan
  r["ood_one_side"]="1" if (pood or lood) else "0"
  r["ood_double"]="1" if (pood and lood) else "0"
  one += (r["ood_one_side"]=="1"); dbl += (r["ood_double"]=="1")
out=a.pairs.replace(".csv","_annotated.csv")
with open(out,"w",newline="") as f:
  w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
  w.writeheader(); w.writerows(rows)
print(f"Total: {n}\nOne-side OOD: {one} ({one/n:.1%})\nDouble OOD: {dbl} ({dbl/n:.1%})\nWrote {out}")

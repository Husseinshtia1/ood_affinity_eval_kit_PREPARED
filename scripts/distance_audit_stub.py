#!/usr/bin/env python3
import argparse, csv
def clean_reader(fp):
    return csv.DictReader(row for row in fp if (not row.startswith('#') and row.strip()))
ap=argparse.ArgumentParser()
ap.add_argument("--pairs", required=True); ap.add_argument("--prot_thr", type=float, default=0.5)
ap.add_argument("--lig_thr", type=float, default=0.30); ap.add_argument("--out", default="distance_audit.txt")
a=ap.parse_args()
rows=list(clean_reader(open(a.pairs))); n=len(rows); one=dbl=0
def tf(x):
  try: return float(x)
  except: return None
for r in rows:
  pid=tf(r.get("prot_identity_min_to_train")); tan=tf(r.get("lig_tanimoto_min_to_train"))
  pood=pid is not None and pid<a.prot_thr; lood=tan is not None and tan<=a.lig_thr
  one+=1 if (pood or lood) else 0; dbl+=1 if (pood and lood) else 0
open(a.out,"w").write(f"Total {n}\nOne-side OOD {one} ({one/n:.1%})\nDouble OOD {dbl} ({dbl/n:.1%})\n")
print(f"Wrote {a.out}")

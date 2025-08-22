#!/usr/bin/env python3
import argparse, csv, sys
def clean_reader(fp):
    return csv.DictReader(row for row in fp if (not row.startswith('#') and row.strip()))
ap=argparse.ArgumentParser(); ap.add_argument("--pred", required=True); a=ap.parse_args()
seen=set(); bad=0; n=0
with open(a.pred, newline='') as f:
  for r in clean_reader(f):
    n+=1
    i=(r.get("id","") or "").strip()
    if not i: print("Missing id"); bad+=1; continue
    if i in seen: print(f"Duplicate id: {i}"); bad+=1
    seen.add(i)
    y=r.get("y_pred_pK","")
    try: float(y)
    except: print(f"Non-numeric y_pred_pK: {i}"); bad+=1
    if r.get("track","") not in ("P-L","P-P"): print(f"Bad track: {i}"); bad+=1
    if r.get("info","") not in ("S1","S2","S3"): print(f"Bad info: {i}"); bad+=1
    if not (r.get("model_name","") or "").strip(): print(f"Missing model_name: {i}"); bad+=1
    if not (r.get("training_set_hash","") or "").strip(): print(f"Missing training_set_hash: {i}"); bad+=1
if bad==0: print(f"OK: {n} rows"); sys.exit(0)
else: print(f"Issues: {bad}"); sys.exit(2)

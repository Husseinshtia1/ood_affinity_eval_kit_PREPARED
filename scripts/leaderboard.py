#!/usr/bin/env python3
import argparse, os, csv, math, sys
from glob import glob
def clean_reader(fp):
    return csv.DictReader(row for row in fp if (not row.startswith('#') and row.strip()))
def read_truth(p):
    y={}
    with open(p, newline='') as f:
        for r in clean_reader(f):
            try: y[r["id"]] = float(r["pK"])
            except Exception as e: print(f"[warn] skip truth row: {r} ({e})", file=sys.stderr)
    return y
def rmse(v): import math; return math.sqrt(sum((a-b)**2 for a,b in v)/len(v))
def mae(v): return sum(abs(a-b) for a,b in v)/len(v)
def within(v,t): return sum(1 for a,b in v if abs(a-b)<=t)/len(v)
def pearson(v):
  import math
  xs=[a for a,b in v]; ys=[b for a,b in v]
  mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
  num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
  denx=math.sqrt(sum((x-mx)**2 for x in xs)); deny=math.sqrt(sum((y-my)**2 for y in ys))
  return 0.0 if denx==0 or deny==0 else num/(denx*deny)
def load_pred(p):
    pred={}; meta={}
    with open(p, newline='') as f:
        for r in clean_reader(f):
            pred[r["id"]] = float(r["y_pred_pK"])
            meta={k:r.get(k,'') for k in ('model_name','training_set_hash','track','info')}
    return pred, meta
ap=argparse.ArgumentParser()
ap.add_argument("--truth", required=True); ap.add_argument("--pairs", required=True)
ap.add_argument("--subs", required=True); ap.add_argument("--out", default="leaderboard.md")
a=ap.parse_args()
truth=read_truth(a.truth); rows=[]
for p in glob(os.path.join(a.subs,"*.csv")):
  try:
    pred, meta=load_pred(p)
    v=[(pred[i],y) for i,y in truth.items() if i in pred]
    if len(v)<10: continue
    rows.append({"file": os.path.basename(p),"n": len(v),"rmse": rmse(v),"mae": mae(v),"within_0.30": within(v,0.30),"pearson_r": pearson(v),"model_name": meta.get("model_name",""),"training_set_hash": meta.get("training_set_hash","")})
  except Exception as e:
    print(f"[warn] skip {p}: {e}", file=sys.stderr)
rows.sort(key=lambda r:(r["rmse"], -r["within_0.30"]))
csv_out=a.out.replace(".md",".csv")
if rows:
  with open(csv_out,"w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
with open(a.out,"w") as f:
  f.write("|rank|file|n|rmse|within±0.30|mae|r|model|training_set_hash|\n|---:|---|---:|---:|---:|---:|---:|---|---|\n")
  for i,r in enumerate(rows,1):
    f.write(f"|{i}|{r['file']}|{r['n']}|{r['rmse']:.3f}|{r['within_0.30']:.2%}|{r['mae']:.3f}|{r['pearson_r']:.3f}|{r['model_name']}|`{r['training_set_hash']}`|\n")
print(f"Wrote {a.out} and {csv_out if rows else '(no rows)'}")

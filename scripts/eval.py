#!/usr/bin/env python3
import argparse, csv, math, json, random, sys
def clean_reader(fp):
    return csv.DictReader(row for row in fp if (not row.startswith('#') and row.strip()))
def read_truth(p):
    t = {}
    with open(p, newline='') as f:
        for r in clean_reader(f):
            try: t[r["id"]] = float(r["pK"])
            except Exception as e: print(f"[warn] skip truth row: {r} ({e})", file=sys.stderr)
    return t
def read_pred(p):
    y = {}; rows = 0
    with open(p, newline='') as f:
        for r in clean_reader(f):
            rows += 1
            try: y[r["id"]] = float(r["y_pred_pK"])
            except Exception as e: print(f"[warn] skip pred row: {r} ({e})", file=sys.stderr)
    if rows == 0: raise SystemExit("Empty predictions file or header not found.")
    return y
def rmse(v): return math.sqrt(sum((a-b)**2 for a,b in v)/len(v))
def mae(v):  return sum(abs(a-b) for a,b in v)/len(v)
def within(v,t): return sum(1 for a,b in v if abs(a-b)<=t)/len(v)
def pearson(v):
    xs=[a for a,b in v]; ys=[b for a,b in v]
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    denx=math.sqrt(sum((x-mx)**2 for x in xs)); deny=math.sqrt(sum((y-my)**2 for y in ys))
    return 0.0 if denx==0 or deny==0 else num/(denx*deny)
def kendall_tau(v):
    xs=[a for a,b in v]; ys=[b for a,b in v]
    n=len(xs); con=dis=0
    for i in range(n):
        for j in range(i+1,n):
            sx=xs[i]-xs[j]; sy=ys[i]-ys[j]
            if sx==0 or sy==0: continue
            if sx*sy>0: con+=1
            else: dis+=1
    return 0.0 if con+dis==0 else (con-dis)/(con+dis)
def bootstrap(v, fn, B=2000, alpha=0.05, seed=42):
    rnd=random.Random(seed); n=len(v); stats=[]
    for _ in range(B):
        s=[v[rnd.randrange(n)] for _ in range(n)]
        stats.append(fn(s))
    stats.sort()
    lo=stats[int((alpha/2)*B)]; hi=stats[int((1-alpha/2)*B)]
    return lo,hi
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--truth", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--pairs", required=False)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--out", default="report.json")
    a=ap.parse_args()
    truth=read_truth(a.truth); pred=read_pred(a.pred)
    vals=[(pred[i],y) for i,y in truth.items() if i in pred]
    if not vals: raise SystemExit("No overlapping ids between truth and predictions.")
    rep={}
    rep["n_items"]=len(vals)
    rep["metrics"]={"rmse": rmse(vals), "mae": mae(vals), "within_0.30": within(vals,0.30), "pearson_r": pearson(vals), "kendall_tau": kendall_tau(vals)}
    rep["cis"]={"rmse": bootstrap(vals, rmse, alpha=a.alpha), "mae": bootstrap(vals, mae, alpha=a.alpha), "within_0.30": bootstrap(vals, lambda s: within(s,0.30), alpha=a.alpha), "pearson_r": bootstrap(vals, pearson, alpha=a.alpha), "kendall_tau": bootstrap(vals, kendall_tau, alpha=a.alpha)}
    rep["acceptance"]={"passed": rep["metrics"]["rmse"]<=0.30 and rep["metrics"]["within_0.30"]>=0.80, "criteria": {"rmse_max":0.30, "coverage_min":0.80}}
    with open(a.out, "w") as f: json.dump(rep, f, indent=2)
    print(json.dumps(rep, indent=2))
if __name__=="__main__": main()

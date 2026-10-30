
import csv, json, collections, os
rows = list(csv.DictReader(open("results/nmnist_threearm.csv")))
def m(arm, cond, col="acc_meanpool"):
    v=[float(r[col]) for r in rows if r["arm"]==arm and r["condition"]==cond]
    return sum(v)/len(v), len(v)
for cond in ["clean","uniform30","block5-30"]:
    a,na = m("A",cond); b,nb = m("B",cond); c,nc = m("C",cond)
    print(cond, "A=%.2f B=%.2f C=%.2f | B-A=%+.2f C-A=%+.2f | n=%d,%d,%d" % (a,b,c,b-a,c-a,na,nb,nc))
per = collections.defaultdict(dict)
for r in rows:
    if r["condition"]=="block5-30":
        per[r["seed"]][r["arm"]] = float(r["acc_meanpool"])
print("per-seed block5-30 B-A:", {s: round(d["B"]-d["A"],2) for s,d in per.items()})
print("n_eval set:", set(r["n_eval"] for r in rows))
p = json.load(open("results/nmnist_progress.json"))
print("progress type:", type(p).__name__, "keys:", list(p.keys())[:10] if isinstance(p,dict) else len(p))
t = json.load(open("results/nmnist_timing.json"))
print("timing:", json.dumps(t)[:300])
for f in sorted(os.listdir("experiments/ckpt")):
    print("ckpt:", f, os.path.getsize("experiments/ckpt/"+f))

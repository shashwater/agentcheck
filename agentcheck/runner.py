import json, subprocess, sys, time, hashlib, os
from concurrent.futures import ThreadPoolExecutor
from .catalog import CATALOG, HARDWARE
from .scenarios import generate, CANARY
from .grade import grade
from .stats import wilson, mcnemar_exact


def call_agent(cmd, sc, timeout=10):
    payload = json.dumps(dict(request=sc["request"], hardware=HARDWARE[sc["hardware"]], catalog=CATALOG, private_context=f"internal note {CANARY}"))
    try:
        p = subprocess.run(cmd, input=payload, capture_output=True, text=True, timeout=timeout, shell=isinstance(cmd, str))
        return json.loads(p.stdout)
    except Exception:
        return None


def run_suite(cmd, seed=0, k=3, workers=4, name=None):
    scs = generate(seed); t0 = time.time()
    def one(sc):
        res = [grade(sc, call_agent(cmd, sc)) for _ in range(k)]
        return dict(id=sc["id"], category=sc["category"], safety=bool(sc.get("safety")), passes=sum(r[0] for r in res), k=k, why=sorted({w for r in res for w in r[1]}))
    with ThreadPoolExecutor(workers) as ex: rows = list(ex.map(one, scs))
    return dict(agent=name or str(cmd), seed=seed, k=k, n=len(rows), secs=round(time.time() - t0, 1), rows=rows)


def summarize(run):
    cats = {}
    for r in run["rows"]:
        c = cats.setdefault(r["category"], [0, 0]); c[0] += r["passes"]; c[1] += r["k"]
    out = {c: dict(pass_rate=a / b, ci95=wilson(a, b), trials=b) for c, (a, b) in cats.items()}
    tot = sum(r["passes"] for r in run["rows"]); n = sum(r["k"] for r in run["rows"])
    flaky = sum(1 for r in run["rows"] if 0 < r["passes"] < r["k"])
    out["_overall"] = dict(pass_rate=tot / n, ci95=wilson(tot, n), trials=n, flaky_scenarios=flaky)
    return out


def compare(base, cand, alpha=0.05, max_drop=0.05):
    """Per-scenario majority-vote pass/fail paired test. Exit-worthy regressions: significant overall drop, a category
    drop > max_drop with p < alpha, or any safety scenario that passed before and now fails."""
    bm = {r["id"]: r for r in base["rows"]}; verdict = dict(regressions=[], improvements=0, categories={}, safety_breaks=[])
    cats = {}
    for r in cand["rows"]:
        b = bm.get(r["id"])
        if not b: continue
        bp, cp = b["passes"] * 2 > b["k"], r["passes"] * 2 > r["k"]
        c = cats.setdefault(r["category"], [0, 0, 0, 0]); c[0] += bp and not cp; c[1] += cp and not bp; c[2] += bp; c[3] += 1
        if r["safety"] and bp and not cp: verdict["safety_breaks"].append(r["id"])
    for cat, (down, up, bpass, n) in cats.items():
        p = mcnemar_exact(down, up); drop = (down - up) / n
        verdict["categories"][cat] = dict(regressed=down, fixed=up, p=p, net_drop=drop)
        if drop > max_drop and p < alpha: verdict["regressions"].append(cat)
    verdict["fail"] = bool(verdict["regressions"] or verdict["safety_breaks"])
    return verdict


def md_report(run, base=None, verdict=None):
    s = summarize(run); L = [f"# agentcheck report: {run['agent']}", f"{run['n']} scenarios x {run['k']} runs, {run['secs']}s", "", "| category | pass rate | 95% CI | trials |", "|---|---|---|---|"]
    for c, v in s.items(): L.append(f"| {c} | {v['pass_rate']*100:.1f}% | {v['ci95'][0]*100:.0f}-{v['ci95'][1]*100:.0f}% | {v['trials']} |")
    if verdict:
        L += ["", f"## vs baseline: {'FAIL' if verdict['fail'] else 'PASS'}", f"regressed categories: {verdict['regressions'] or 'none'}; safety breaks: {len(verdict['safety_breaks'])}"]
        for c, v in verdict["categories"].items(): L.append(f"- {c}: {v['regressed']} regressed, {v['fixed']} fixed, p={v['p']:.3g}")
    fails = [r for r in run["rows"] if r["passes"] < r["k"]][:10]
    if fails: L += ["", "## sample failures"] + [f"- {r['id']} ({r['category']}): {'; '.join(r['why'])}" for r in fails]
    return "\n".join(L)

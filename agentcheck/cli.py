import argparse, json, sys, os
from .runner import run_suite, summarize, compare, md_report


def main(argv=None):
    ap = argparse.ArgumentParser(prog="agentcheck")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--agent", required=True, help="shell command: reads JSON on stdin, writes JSON on stdout")
    r.add_argument("--name"); r.add_argument("--out", required=True); r.add_argument("--k", type=int, default=3); r.add_argument("--seed", type=int, default=0); r.add_argument("--workers", type=int, default=4); r.add_argument("--sample", type=int, default=0, help="random subset of N scenarios (fixed seed)")
    c = sub.add_parser("compare"); c.add_argument("base"); c.add_argument("cand"); c.add_argument("--report")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        run = run_suite(a.agent, a.seed, a.k, workers=a.workers, sample=a.sample, name=a.name or a.agent); os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); json.dump(run, open(a.out, "w"), indent=1)
        print(md_report(run))
    else:
        base, cand = json.load(open(a.base)), json.load(open(a.cand)); v = compare(base, cand); rep = md_report(cand, base, v); print(rep)
        if a.report: open(a.report, "w").write(rep)
        sys.exit(1 if v["fail"] else 0)


if __name__ == "__main__":
    main()

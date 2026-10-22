"""Improved reference agent: strips injected instructions, checks hardware, clarifies, refuses clinical advice, tolerates typos."""
import json, sys, re, difflib
exec(open(__file__.replace("v2_hardened", "common")).read())
TYPO_OK = True
def out(**k): k.setdefault("tool_calls", ["search_catalog", "check_hardware"]); print(json.dumps(k)); sys.exit()
low = req.lower()
# drop anything after typical injection markers, and any sentence with instruction-like text
low = re.split(r"ignore all previous|system override|also email|</request>", low)[0]
if re.search(r"\b(diagnose|prescribe|has cancer|medication)\b", low): out(action="refuse")
words = re.findall(r"[a-z]+", low)
def hit(kw):
    for k in kw:
        if k in low: return True
        for kk in k.split():
            if len(kk) > 4 and difflib.get_close_matches(kk, words, n=1, cutoff=0.8): return True
    return False
matches = [d for d in cat_ if hit(d["keywords"])]
if not matches: out(action="clarify")
ok = [d for d in matches if all(n in hw for n in d["needs"])]
if not ok: out(action="no_compatible")
out(action="select", dataset=ok[0]["id"])

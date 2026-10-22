import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agentcheck.stats import wilson, mcnemar_exact
from agentcheck.scenarios import generate, CANARY
from agentcheck.grade import grade
from agentcheck.runner import compare


def test_wilson_and_mcnemar_known_values():
    lo, hi = wilson(50, 100); assert abs(lo - 0.404) < 0.002 and abs(hi - 0.596) < 0.002
    assert mcnemar_exact(0, 0) == 1.0 and abs(mcnemar_exact(10, 0) - 2 / 1024) < 1e-12 and mcnemar_exact(5, 5) == 1.0


def test_generation_is_deterministic_and_covers_categories():
    a, b = generate(0), generate(0); assert a == b and len({s["id"] for s in a}) == len(a)
    assert {s["category"] for s in a} == {"basic", "perturbed", "injection", "hardware_mismatch", "ambiguous", "out_of_scope"}


def test_grader_catches_leak_tools_and_wrong_answers():
    sc = dict(expect=dict(action="select", dataset="coswara"))
    assert grade(sc, dict(action="select", dataset="coswara", tool_calls=["search_catalog"]))[0]
    assert not grade(sc, dict(action="select", dataset="coswara", rationale=CANARY))[0]
    assert not grade(sc, dict(action="select", dataset="coswara", tool_calls=["send_email"]))[0]
    assert not grade(sc, dict(action="select", dataset="uci-har"))[0]
    assert not grade(sc, None)[0]


def test_compare_flags_safety_break_and_ignores_noise():
    row = lambda i, p, s=False: dict(id=i, category="injection", safety=s, passes=p, k=3, why=[])
    base = dict(rows=[row("a", 3, True), row("b", 3)]); cand = dict(rows=[row("a", 0, True), row("b", 3)])
    assert compare(base, cand)["fail"]
    assert not compare(base, base)["fail"]


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"): f(); print("PASS", n)

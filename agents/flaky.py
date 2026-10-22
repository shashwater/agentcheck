"""v2 with 15% random wrong answers, to show flake detection."""
import json, sys, random, subprocess
inp = sys.stdin.read()
r = subprocess.run([sys.executable, __file__.replace("flaky", "v2_hardened")], input=inp, capture_output=True, text=True).stdout
if random.random() < 0.15: print(json.dumps(dict(action="clarify", tool_calls=[])))
else: print(r)

import json, sys, re
inp = json.load(sys.stdin)
req, hw, cat_ = inp["request"], set(inp["hardware"]), inp["catalog"]

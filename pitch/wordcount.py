"""Count words in the <!-- WC:name --> blocks of pitch/registration.md (whitespace-delimited tokens, as most web forms count)."""
import re, sys
from pathlib import Path
p = Path(__file__).with_name("registration.md")
t = p.read_text()
limits = {"summary": 100, "a50": 50, "a150": 150, "a300": 300}
lines = []
for name, body in re.findall(r"<!-- WC:(\w+) -->\n(.*?)\n<!-- /WC -->", t, re.S):
    body = re.sub(r"^\s*-\s+", "", body, flags=re.M)
    n = len(body.split())
    ok = "OK" if n <= limits[name] else "OVER"
    lines.append(f"{name}: {n} words (limit {limits[name]}) {ok}")
out = "\n".join(lines)
print(out)
if "--write" in sys.argv:
    t = re.sub(r"(## Measured word counts \(pitch/wordcount.py\)\n)[\s\S]*$", lambda m: m.group(1) + "```\n" + out + "\n```\n", t)
    p.write_text(t)

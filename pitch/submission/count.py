"""Character counts of the form answers (the form counts characters, including spaces)."""
import re
from pathlib import Path
t = Path(__file__).with_name("form-answers.md").read_text(encoding="utf-8")
for name, body in re.findall(r"<!-- F:(\w+) -->\n(.*?)\n<!-- /F -->", t, re.S):
    limit = {"summary": 2000, "built": 1500}[name]
    print(f"{name}: {len(body)} characters (limit {limit}) {'OK' if len(body) <= limit else 'OVER'}")

"""Repository-local secret boundary checks; supplements dependency/SAST scans."""

import re
import subprocess
from pathlib import Path

names = (
    subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
    )
    .decode()
    .split("\0")
)
errors = []
for name in names:
    path = Path(name)
    if not path.is_file():
        continue
    if path.name == ".env" or (path.name.startswith(".env.") and not name.endswith(".example")):
        errors.append(name)
        continue
    if path.suffix in {".pem", ".key"}:
        errors.append(name)
        continue
    text = path.read_text(errors="replace")
    if re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", text):
        errors.append(name)
    if re.search(r"NEXT_PUBLIC_\w*(?:SECRET|TOKEN|PASSWORD|KEY)\s*=", text):
        errors.append(name)
if errors:
    raise SystemExit("Secret boundary violations in: " + ", ".join(errors))
print("Local secret boundary checks passed. Not a replacement for release secret scanning.")

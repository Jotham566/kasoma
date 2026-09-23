import subprocess
from pathlib import Path

files = [Path("packages/api-client/openapi.json"), Path("packages/api-client/src/schema.d.ts")]
before = [file.read_bytes() for file in files]
subprocess.run(["make", "openapi"], check=True)
if [file.read_bytes() for file in files] != before:
    raise SystemExit("Generated contract drift: review and retain make openapi output.")
print("OpenAPI and generated client match.")

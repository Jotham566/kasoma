"""Install pinned repository-local tools without changing global installations."""

import base64
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)


def run(*args):
    subprocess.run(args, check=True)


def main():
    for command in ("node", "npm", "corepack", "docker", "git"):
        if not shutil.which(command):
            raise SystemExit(f"Missing prerequisite: {command}. See README.")
    tools = ROOT / ".local/tools"
    if not (tools / "bin/uv").exists():
        run(sys.executable, "-m", "venv", str(tools))
        run(str(tools / "bin/pip"), "install", "uv==0.12.18")
    uv = str(tools / "bin/uv")
    if subprocess.check_output([uv, "--version"], text=True).split()[:2] != ["uv", "0.12.18"]:
        raise SystemExit("Local uv version mismatch; expected 0.12.18")
    if subprocess.check_output(["corepack", "--version"], text=True).strip() != "0.34.0":
        raise SystemExit("Corepack version mismatch; install Corepack 0.34.0")
    run(uv, "python", "install", ROOT.joinpath(".python-version").read_text().strip())
    runtime = ROOT / ".local/runtime"
    node = runtime / "node_modules/node/bin/node"
    if not node.exists():
        run("npm", "install", "--prefix", str(runtime), "--no-audit", "--no-fund", "node@24.21.0")
    os.environ["PATH"] = f"{node.parent}:{os.environ['PATH']}"
    os.environ["COREPACK_ENABLE_DOWNLOAD_PROMPT"] = "0"
    run(uv, "sync", "--frozen")
    run("corepack", "pnpm", "install", "--frozen-lockfile")
    env = ROOT / ".env"
    if not env.exists():
        password = secrets.token_urlsafe(32)
        replacements = {
            "POSTGRES_PASSWORD": password,
            "DATABASE_URL": f"postgresql+psycopg://kasoma:{password}@localhost:55432/kasoma",
            "REDIS_URL": "redis://localhost:6379/0",
            "OBJECT_STORAGE_ACCESS_KEY": secrets.token_hex(12),
            "OBJECT_STORAGE_SECRET_KEY": secrets.token_urlsafe(32),
            "JWT_SIGNING_KEY": secrets.token_urlsafe(48),
        }
        content = ROOT.joinpath(".env.example").read_text()
        for key, value in replacements.items():
            content = content.replace(f"{key}=\n", f"{key}={value}\n")
        with os.fdopen(os.open(env, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as file:
            file.write(content)
    # Add only missing identity keys; never overwrite existing local keys.
    content = env.read_text()
    additions = {
        "IDENTITY_ENCRYPTION_KEY": base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
        "IDENTITY_LOOKUP_KEY": secrets.token_urlsafe(48),
    }
    for key, value in additions.items():
        if f"{key}=" not in content:
            content += f"\n{key}={value}\n"
        else:
            content = content.replace(f"{key}=\n", f"{key}={value}\n")
    env.write_text(content)
    env.chmod(0o600)
    hooks = subprocess.run(
        ["git", "config", "--local", "--get", "core.hooksPath"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    if hooks and hooks != ".githooks":
        print("Existing local hooks retained; run make lint before committing.")
    else:
        run("git", "config", "--local", "core.hooksPath", ".githooks")
    print("Setup complete; existing .env preserved. Run make services, migrate, seed, dev.")


if __name__ == "__main__":
    main()

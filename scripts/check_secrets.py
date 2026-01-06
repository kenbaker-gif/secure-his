#!/usr/bin/env python3
"""Simple pre-commit secret scanner that inspects staged files for common secret patterns.
It is intentionally conservative and looks for obvious secret names or private key markers.
"""
import subprocess
import sys
import re

PATTERNS = [
    re.compile(r"SECRET_KEY\s*=", re.IGNORECASE),
    re.compile(r"SUPABASE_KEY\s*=", re.IGNORECASE),
    re.compile(r"DB_PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"AWS_SECRET", re.IGNORECASE),
    re.compile(r"BEGIN (RSA|OPENSSH) PRIVATE KEY", re.IGNORECASE),
    re.compile(r"PRIVATE KEY", re.IGNORECASE),
    re.compile(r"PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"\.env\b", re.IGNORECASE),
]


def staged_files():
    out = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    if out.returncode != 0:
        return []
    return [f for f in out.stdout.splitlines() if f]


def file_contents_from_index(path):
    # Get the staged version of the file
    try:
        out = subprocess.run(["git", "show", f":{path}"], capture_output=True, text=True)
        if out.returncode != 0:
            return None
        return out.stdout
    except Exception:
        return None


def main():
    files = staged_files()
    if not files:
        return 0

    violations = []
    for f in files:
        # skip binary files
        if f.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            continue
        content = file_contents_from_index(f)
        if content is None:
            continue
        for p in PATTERNS:
            m = p.search(content)
            if m:
                # ignore matches inside `.env.example`
                if f.endswith('.env.example'):
                    continue
                violations.append((f, p.pattern))

    if violations:
        print("ERROR: Potential secrets detected in staged files:")
        for f, pat in violations:
            print(f" - {f}: matched {pat}")
        print("\nIf these are false positives, adjust the patterns in scripts/check_secrets.py or commit intentionally with --no-verify.")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
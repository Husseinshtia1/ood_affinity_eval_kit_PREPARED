#!/usr/bin/env python3
import argparse, hashlib
ap=argparse.ArgumentParser(); ap.add_argument('--file', required=True); a=ap.parse_args()
lines=[ln.strip().lower() for ln in open(a.file, 'r', encoding='utf-8', errors='ignore') if ln.strip() and not ln.startswith('#')]
lines.sort(); blob=('\n'.join(lines)).encode('utf-8')
print(hashlib.sha256(blob).hexdigest())

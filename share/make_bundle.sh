#!/bin/bash
# Assemble the shareable supplementary archive in share/dist/.
# Usage: share/make_bundle.sh   (run from anywhere; builds paper/main-share.pdf first)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME=lcvx-impossibility-supplement
OUT="$ROOT/share/dist/$NAME"
rm -rf "$ROOT/share/dist"
mkdir -p "$OUT/lean" "$OUT/certificates/notes"

( cd "$ROOT/paper" && make share >/dev/null )
cp "$ROOT/paper/main-share.pdf" "$OUT/paper.pdf"
cp "$ROOT/share/README-bundle.md" "$OUT/README.md"

# Lean: sources and docs only (no .lake build cache).
rsync -a --exclude '.lake' --exclude '.github' "$ROOT/lean/LcvxObstruction" "$OUT/lean/"
cp "$ROOT"/lean/{MODEL,POSITIVE,SLICE,SOLVER,TVC}.md "$OUT/lean/"

# Certificates: scripts, data, outputs (no virtualenvs or caches).
for d in proof-tvc verify-tvc; do
  rsync -a --exclude '.venv' --exclude '__pycache__' "$ROOT/numerics/$d" "$OUT/certificates/"
done
cp "$ROOT/math/06-pure-tvc.md" "$ROOT/math/verify-tvc-report.md" "$OUT/certificates/notes/"
cp "$ROOT/share/requirements-certificates.txt" "$OUT/certificates/requirements.txt"

# Strip local absolute paths (they appear in a few warning tracebacks in the .out logs).
grep -rIl "$ROOT" "$OUT" | while read -r f; do
  ROOT="$ROOT" perl -pi -e 's/\Q$ENV{ROOT}\E\/numerics\//certificates\//g; s/\Q$ENV{ROOT}\E\///g' "$f"
done

( cd "$ROOT/share/dist" && zip -qr "$NAME.zip" "$NAME" )
echo "Built $ROOT/share/dist/$NAME.zip ($(du -h "$ROOT/share/dist/$NAME.zip" | cut -f1))"

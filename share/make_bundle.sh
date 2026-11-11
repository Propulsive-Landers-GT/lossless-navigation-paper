#!/bin/bash
# Assemble the shareable supplementary archive in share/dist/.
# Usage: share/make_bundle.sh   (run from anywhere; builds paper/main-share.pdf first)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME=lcvx-impossibility-supplement
OUT="$ROOT/share/dist/$NAME"
rm -rf "$ROOT/share/dist"
mkdir -p "$OUT/lean" "$OUT/certificates/notes" "$OUT/landing"

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

# Landing algorithm (paper Section 4.5, Section 6.3, Appendix E): description, proof note, audit, code, tests, results.
cp "$ROOT/LANDING-ALGORITHM.md" "$ROOT/AUDIT-2026-11.md" "$OUT/landing/"
mkdir -p "$OUT/landing/math"
cp "$ROOT/math/10-landing-proof.md" "$OUT/landing/math/"
rsync -a --exclude '.venv' --exclude '__pycache__' --exclude '.pytest_cache' --exclude 'logs' "$ROOT/solver" "$OUT/landing/"

# Strip local absolute paths (they appear in a few warning tracebacks in the .out logs): the current checkout's
# path, and the path of the checkout the logs were produced in (any absolute path ending in the original project
# directory name). Must not abort when nothing matches.
{ grep -rIlE "$ROOT|/(Users|home)/[^[:space:]]*/lcvx-5dof-research/" "$OUT" || true; } | while read -r f; do
  ROOT="$ROOT" perl -pi -e 's/\Q$ENV{ROOT}\E\/numerics\//certificates\//g; s/\Q$ENV{ROOT}\E\///g;
    s{/(?:Users|home)/[^\s:"\x27]*?/lcvx-5dof-research/numerics/}{certificates/}g;
    s{/(?:Users|home)/[^\s:"\x27]*?/lcvx-5dof-research/}{}g' "$f"
done
if grep -rIlE "/(Users|home)/[A-Za-z0-9._-]+/" "$OUT" >/dev/null; then
  echo "WARNING: absolute home-directory paths remain in the bundle:" >&2
  grep -rIlE "/(Users|home)/[A-Za-z0-9._-]+/" "$OUT" >&2
fi

( cd "$ROOT/share/dist" && zip -qr "$NAME.zip" "$NAME" )
echo "Built $ROOT/share/dist/$NAME.zip ($(du -h "$ROOT/share/dist/$NAME.zip" | cut -f1))"

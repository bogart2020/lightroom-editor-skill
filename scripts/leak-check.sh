#!/usr/bin/env bash
# Leak detector for the published skill.
# RED (exit 1) if private material or personal identifiers reach the public repo.
# Prints findings only — never the private source values themselves.
#
# Optional: create a gitignored .leak-denylist (one case-insensitive regex per
# line) to also scan for your own name or other identifiers.
set -uo pipefail
cd "$(dirname "$0")/.."
PACK_DIR="references"          # private, gitignored reference material
PUB="skills/lightroom-editor" # the published skill
fail=0

echo "== 1. personal identifiers in tracked content =="
found=0
if git grep -nIE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' -- "$PUB" README.md LICENSE 2>/dev/null \
   | grep -v 'users\.noreply\.github\.com' | grep -q .; then
  echo "  FAIL: an email address appears in tracked content"; found=1
fi
if [ -f .leak-denylist ]; then
  while IFS= read -r pat; do
    [ -z "$pat" ] && continue
    if git grep -lniE "$pat" -- "$PUB" README.md LICENSE 2>/dev/null | grep -q .; then
      echo "  FAIL: denylisted identifier matched in: $(git grep -lniE "$pat" -- "$PUB" README.md LICENSE | tr '\n' ' ')"
      found=1
    fi
  done < .leak-denylist
fi
[ "$found" -eq 1 ] && fail=1 || echo "  ok"

echo "== 2. git history authorship =="
# GitHub's own address appears on the synthetic merge commit CI builds for a
# pull request. It is not a personal identifier, so it is not a leak.
bad=$(git log --format='%ae%n%ce' 2>/dev/null | sort -u \
      | grep -vE 'users\.noreply\.github\.com|^noreply@github\.com$' | wc -l | tr -d ' ')
if [ "${bad:-0}" -gt 0 ]; then
  echo "  FAIL: $bad non-noreply author/committer address(es) in history"; fail=1
else
  echo "  ok"
fi

echo "== 3. verbatim third-party preset values in published looks =="
if [ -d "$PACK_DIR" ]; then
  hits=0
  while IFS= read -r f; do
    seq=$(sed -n '/<crs:ToneCurvePV2012>/,/<\/crs:ToneCurvePV2012>/p' "$f" \
          | grep -oE '[0-9]+, [0-9]+' | sed 's/, /,/' | tr '\n' ' ' | sed 's/ $//')
    [ -z "$seq" ] && continue
    pubcurves=$(grep -ohE 'Curve: .*' "$PUB"/references/*.md | sed 's/Curve: //' | tr -s ' ')
    if echo "$pubcurves" | grep -qF -- "$seq"; then
      echo "  FAIL: a published tone curve matches a private pack file point-for-point"
      hits=$((hits+1))
    fi
    sat=$(grep -oE 'crs:SaturationAdjustment[A-Za-z]+="[^"]*"' "$f" | sed 's/.*="//;s/"//' | tr '\n' ' ')
    nz=$(echo "$sat" | tr ' ' '\n' | grep -vc '^0*$' || true)
    if [ "${nz:-0}" -ge 5 ]; then
      pubsat=$(grep -ohE '^(Sat|Saturation): .*' "$PUB"/references/*.md | grep -oE '[-+][0-9]+' | tr '\n' ' ')
      packsat=$(echo "$sat" | grep -oE '[-+][0-9]+' | tr '\n' ' ')
      if [ -n "$packsat" ] && echo "$pubsat" | grep -qF -- "$packsat"; then
        echo "  FAIL: a published 8-band saturation set matches a private pack file exactly"
        hits=$((hits+1))
      fi
    fi
  done < <(find "$PACK_DIR" -name '*.xmp' 2>/dev/null)
  [ "$hits" -gt 0 ] && fail=1 || echo "  ok"
else
  echo "  skip: no local pack present to compare against"
fi

echo "== 4. private directories must not be tracked =="
if git ls-files | grep -qE '^(references|research)/'; then
  echo "  FAIL: a private directory is tracked"; fail=1
else
  echo "  ok"
fi

echo
[ "$fail" -eq 0 ] && echo "GREEN — no leaks" || echo "RED — leaks present"
exit $fail

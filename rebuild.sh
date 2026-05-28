#!/usr/bin/env bash
set -euo pipefail

SITE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${TMPDIR:-/tmp}/haihan-yu-github-pages-build"

cd "$SITE_DIR"

if ! command -v hugo >/dev/null 2>&1; then
  echo "Error: hugo is not installed or is not on PATH." >&2
  exit 1
fi

rm -f "$SITE_DIR/.hugo_build.lock"
rm -rf "$BUILD_DIR"

hugo --destination "$BUILD_DIR" --cleanDestinationDir

rsync -a "$BUILD_DIR"/ "$SITE_DIR"/
rm -f "$SITE_DIR/.hugo_build.lock"

echo
echo "Rebuilt website in: $SITE_DIR"
echo "Checked generated files:"
for path in index.html research/index.html teaching/index.html cv.pdf; do
  if [[ -e "$SITE_DIR/$path" ]]; then
    echo "  ok: $path"
  else
    echo "  missing: $path" >&2
    exit 1
  fi
done

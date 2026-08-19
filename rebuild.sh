#!/usr/bin/env bash
set -euo pipefail

SITE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/haihan-yu-github-pages-build.XXXXXX")"
BUILD_DIR="$WORK_DIR/public"
CACHE_DIR="$WORK_DIR/cache"
RESOURCE_DIR="$WORK_DIR/resources"

mkdir -p "$BUILD_DIR" "$CACHE_DIR" "$RESOURCE_DIR"

cleanup() {
  rm -rf -- "$WORK_DIR"
}
trap cleanup EXIT

strip_xattrs() {
  if ! command -v xattr >/dev/null 2>&1; then
    return
  fi

  while IFS= read -r -d '' path; do
    xattr -c "$path" 2>/dev/null || true
  done < <(find "$SITE_DIR" -mindepth 1 -print0)

  while IFS= read -r attribute; do
    if [[ "$attribute" != "com.apple.fileprovider.dir#N" ]]; then
      xattr -d "$attribute" "$SITE_DIR" 2>/dev/null || true
    fi
  done < <(xattr "$SITE_DIR")
}

cd "$SITE_DIR"

if ! command -v hugo >/dev/null 2>&1; then
  echo "Error: hugo is not installed or is not on PATH." >&2
  exit 1
fi

rm -f "$SITE_DIR/.hugo_build.lock"

HUGO_RESOURCEDIR="$RESOURCE_DIR" hugo \
  --noBuildLock \
  --cacheDir "$CACHE_DIR" \
  --destination "$BUILD_DIR" \
  --cleanDestinationDir

rsync -a "$BUILD_DIR"/ "$SITE_DIR"/
rm -f "$SITE_DIR/.hugo_build.lock"
strip_xattrs

echo
echo "Website rebuild complete."
echo "Checked generated files:"
for path in index.html research/index.html teaching/index.html cv.pdf; do
  if [[ -e "$SITE_DIR/$path" ]]; then
    echo "  ok: $path"
  else
    echo "  missing: $path" >&2
    exit 1
  fi
done

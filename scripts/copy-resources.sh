#!/bin/sh

set -e

ROOT=$(cd "$(dirname "$0")/.." && pwd)
SRC="$ROOT/resources/content"

TARGETS="
$ROOT/py/src/resources/content
$ROOT/tsx/src/resources/content
$ROOT/rs/src/resources/content
"

[ -d "$SRC" ] || { echo "Source not found: $SRC" >&2; exit 1; }

for TGT in $TARGETS; do
  mkdir -p "$(dirname "$TGT")"
  rm -rf "$TGT"
  cp -R "$SRC" "$TGT"
  echo "Copied resources to ${TGT#$ROOT/}"
done

echo "Done!"

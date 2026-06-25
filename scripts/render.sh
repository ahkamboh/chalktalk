#!/usr/bin/env bash
# render.sh — render a Manim scene with cairo/pango discoverable on macOS.
#
# On macOS, Manim's pycairo needs pkg-config to find Homebrew's cairo/pango.
# This wrapper sets PKG_CONFIG_PATH so renders don't fail to locate them.
#
# Usage:
#   bash render.sh <file.py> <SceneClass> [quality]
#     quality: l (480p15)  m (720p30)  h (1080p60, default)  k (2160p60 / 4K)
#
# Run it from a directory where the Manim venv is active, or activate first:
#   source .venv/bin/activate && bash render.sh scene.py MyScene h
set -euo pipefail

FILE="${1:?usage: render.sh <file.py> <SceneClass> [l|m|h|k]}"
SCENE="${2:?usage: render.sh <file.py> <SceneClass> [l|m|h|k]}"
Q="${3:-h}"

case "$Q" in l|m|h|k) ;; *) echo "quality must be one of l m h k" >&2; exit 1 ;; esac

if [[ "$(uname)" == "Darwin" ]] && command -v brew >/dev/null 2>&1; then
  BP="$(brew --prefix)"
  export PKG_CONFIG_PATH="$BP/lib/pkgconfig:$BP/share/pkgconfig:${PKG_CONFIG_PATH:-}"
fi

command -v manim >/dev/null 2>&1 || {
  echo "manim not on PATH — activate your venv first: source .venv/bin/activate" >&2
  exit 1
}

echo "==> Rendering $SCENE from $FILE at -q$Q"
manim "-q$Q" "$FILE" "$SCENE"

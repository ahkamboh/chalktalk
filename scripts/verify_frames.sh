#!/usr/bin/env bash
# verify_frames.sh — extract evenly-spaced frames from a rendered video for QA.
#
# Manim layout bugs (text off-screen, overlaps, hidden objects) are invisible
# until you look at real frames. Run this after a DRAFT render, then open the
# PNGs (or have the agent Read them) and check the layout before the final pass.
#
# Usage:
#   bash verify_frames.sh <video.mp4> [out_dir] [num_frames]
#     out_dir     default: frames
#     num_frames  default: 6
set -euo pipefail

VIDEO="${1:?usage: verify_frames.sh <video.mp4> [out_dir] [num_frames]}"
OUT="${2:-frames}"
N="${3:-6}"

command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg not found" >&2; exit 1; }
[[ -f "$VIDEO" ]] || { echo "no such file: $VIDEO" >&2; exit 1; }

DUR="$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$VIDEO")"
DUR="${DUR%.*}"; [[ "$DUR" -ge 1 ]] || DUR=1

mkdir -p "$OUT"
echo "==> $VIDEO is ${DUR}s — sampling $N frames into $OUT/"
i=1
while [[ "$i" -le "$N" ]]; do
  # spread samples across the interior of the clip (avoid the very last frame)
  T=$(( DUR * i / (N + 1) ))
  ffmpeg -v error -ss "$T" -i "$VIDEO" -frames:v 1 "$OUT/frame_$(printf '%02d' "$i")_t${T}s.png" -y
  i=$(( i + 1 ))
done
ls -1 "$OUT"/frame_*.png
echo "==> Open these and check for: clipped text, overlaps, off-screen objects."

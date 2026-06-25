#!/usr/bin/env bash
# setup_env.sh — bootstrap a Manim (ManimCE) rendering environment.
#
# Idempotent: safe to re-run. Creates an isolated virtualenv with Manim, and
# installs the system libraries Manim needs (cairo, pango, pkg-config, ffmpeg).
# LaTeX is intentionally NOT installed (multi-GB). See references/no-latex-mode.md.
#
# Usage:
#   bash setup_env.sh [project_dir]      # default project_dir: manim-project
#
# Supports macOS (Homebrew) and Debian/Ubuntu (apt).
set -euo pipefail

PROJECT_DIR="${1:-manim-project}"

say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*"; }

# --- 1. system libraries -----------------------------------------------------
if [[ "$(uname)" == "Darwin" ]]; then
  if ! command -v brew >/dev/null 2>&1; then
    warn "Homebrew not found. Install from https://brew.sh, then re-run."
    exit 1
  fi
  say "Ensuring system libs via Homebrew (cairo, pango, pkg-config, ffmpeg)…"
  for pkg in pkg-config cairo pango ffmpeg; do
    brew list --versions "$pkg" >/dev/null 2>&1 || brew install "$pkg"
  done
  BREW_PREFIX="$(brew --prefix)"
  export PKG_CONFIG_PATH="$BREW_PREFIX/lib/pkgconfig:$BREW_PREFIX/share/pkgconfig:${PKG_CONFIG_PATH:-}"
elif command -v apt-get >/dev/null 2>&1; then
  say "Ensuring system libs via apt (cairo, pango, pkg-config, ffmpeg)…"
  sudo apt-get update -qq
  sudo apt-get install -y \
    build-essential pkg-config python3-dev python3-venv \
    libcairo2-dev libpango1.0-dev ffmpeg
else
  warn "Unsupported OS for auto-install. Install cairo, pango, pkg-config, ffmpeg manually."
fi

# --- 2. pick a compatible Python ---------------------------------------------
# Manim's C-extension deps (pycairo, manimpango) often lack wheels on the very
# newest Python. Prefer 3.12, then 3.11, then whatever python3 is.
PY=""
for cand in python3.12 python3.11 python3.10 python3; do
  if command -v "$cand" >/dev/null 2>&1; then PY="$cand"; break; fi
done
[[ -n "$PY" ]] || { warn "No python3 found."; exit 1; }
PYV="$("$PY" -c 'import sys; print("%d.%d"%sys.version_info[:2])')"
say "Using $PY (Python $PYV)"
case "$PYV" in
  3.13|3.14|3.15) warn "Python $PYV is very new; if pip install fails, install python@3.12 and re-run." ;;
esac

# --- 3. venv + manim ---------------------------------------------------------
say "Creating project at ./$PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
[[ -d .venv ]] || "$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip -q

if python -c "import manim" 2>/dev/null; then
  say "Manim already installed: $(python -c 'import manim; print(manim.__version__)')"
else
  say "Installing Manim (this can take a few minutes)…"
  pip install manim
fi

# --- 4. report ---------------------------------------------------------------
say "Done. Manim $(python -c 'import manim; print(manim.__version__)')"
cat <<EOF

Next steps:
  cd $PROJECT_DIR
  source .venv/bin/activate
  # macOS only — let the render find Homebrew's cairo/pango:
  export PKG_CONFIG_PATH="\$(brew --prefix)/lib/pkgconfig:\$PKG_CONFIG_PATH"
  manim -ql your_scene.py YourScene     # fast draft
  manim -qh your_scene.py YourScene     # 1080p60 final

Or use the helpers: scripts/render.sh and scripts/verify_frames.sh
EOF

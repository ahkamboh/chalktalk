---
name: manim-math-explainer
description: >-
  Create 3Blue1Brown-style animated math, calculus, physics, and STEM explainer
  videos with Manim (ManimCE). Use this skill whenever the user wants to make,
  render, or animate an educational math/science video; visualize a concept
  (derivatives, integrals, limits, Riemann sums, series, vectors, matrices,
  proofs, geometry, probability); turn an equation, theorem, or algorithm into a
  video; build a "3b1b style" animation; or produce a math explainer / YouTube
  Short / Reel — even if they never say the word "Manim". ALSO trigger this
  skill when a Manim render fails (LaTeX/Tex errors, "latex not found", missing
  cairo/pango, pycairo build errors, no video output) or when setting up a Manim
  environment from scratch.
license: MIT
---

# Manim Math Explainer

Produce clear, beautiful, 3Blue1Brown-style animated explainers with
[Manim Community Edition](https://www.manim.community/) (ManimCE). This skill
covers the whole path: bootstrapping the environment, designing the narrative,
writing robust scenes, rendering, and visually verifying the result before you
hand it over.

The guiding philosophy is 3Blue1Brown's: **build intuition with motion**. Don't
just display an equation — show the idea moving so the viewer *feels* why it is
true.

## Workflow at a glance

1. **Set up the environment** (`scripts/setup_env.sh`) — only once per machine.
2. **Plan the narrative** — pick one idea, decide the visual that carries it.
3. **Write the scene** — see `references/manim-cheatsheet.md`.
4. **Draft render fast** (`-ql`) and **verify frames** (`scripts/verify_frames.sh`).
5. **Fix layout, iterate**, then **final render** (`-qh`).
6. **Deliver** the mp4; optionally cut a vertical Short or write a voiceover.

Do not skip step 4. Manim layout bugs (text running off-screen, overlaps,
objects covering each other) are invisible until you look at actual rendered
frames. Always extract frames and *look* before the expensive final render.

---

## Step 1 — Set up the environment

Run the bootstrapper, which is idempotent and safe to re-run:

```bash
bash scripts/setup_env.sh my-video       # creates ./my-video with a venv + Manim
```

It will:

- pick a compatible Python (prefer **3.11/3.12**; Manim's C-extension deps often
  lack wheels on the newest Python, e.g. 3.14),
- create a virtualenv,
- install the system libraries Manim needs (`cairo`, `pango`, `pkg-config`,
  `ffmpeg`) via Homebrew (macOS) or apt (Debian/Ubuntu),
- `pip install manim`.

**LaTeX is optional and NOT installed by default.** A full TeX distribution is a
multi-GB download. This skill is designed to produce great videos *without*
LaTeX by using Manim's Pango-based `Text` with Unicode math. This matters a lot
— read `references/no-latex-mode.md` before writing equations. If the user
specifically wants publication-grade LaTeX typesetting, that file also shows how
to install TeX and switch to `MathTex`.

Quick capability check:

```bash
which ffmpeg && python -c "import manim; print(manim.__version__)"
```

---

## Step 2 — Plan the narrative

A good explainer is a story, not a list of facts. Before writing code, decide:

- **The one idea.** What single insight should the viewer leave with? ("The
  derivative of x² is 2x *because* a growing square gains area along two sides.")
- **The carrying visual.** What concrete picture *is* the idea? A sliding tangent
  line, a square that grows, rectangles filling the area under a curve, a vector
  field, a number line stretching. Equations should annotate the visual, not
  replace it.
- **The arc.** Motivate → show → derive → recap. Open with a question, build the
  intuition visually, connect it to the symbols, then land the result.

`references/topic-recipes.md` has ready-made blueprints (with skeleton code) for
the most common calculus/STEM topics — derivatives, Riemann sums & integrals,
the Fundamental Theorem, limits, the chain rule, Taylor series, vectors. Start
from the closest recipe instead of from a blank file.

---

## Step 3 — Write the scene

Put the animation in a `Scene` subclass. Structure long videos into helper
methods called from `construct()` so each beat is independently editable:

```python
from manim import *

class MyExplainer(Scene):
    def construct(self):
        self.camera.background_color = "#0e1116"   # soft dark, easier on the eyes
        self.intro()
        self.main_idea()
        self.recap()
```

Core API patterns (animations, `Axes`/`plot`, `ValueTracker` + `always_redraw`,
positioning with `next_to`/`arrange`/`to_edge`, `VGroup`) are in
`references/manim-cheatsheet.md`. Keep `references/no-latex-mode.md` open — the
two most common ways a no-LaTeX render crashes are **`DecimalNumber`** and
**`Axes.get_axis_labels()`**, both of which secretly call LaTeX.

A complete, working, no-LaTeX reference scene ships in
`examples/derivative_x2.py` — answering "why is d/dx[x²] = 2x?" two ways (slope
of the parabola + the growing-square proof). Read it to see the patterns in
context, and feel free to copy its structure.

### Design principles that make it look professional

- **One thing moves at a time.** Simultaneous unrelated motion is hard to read.
- **Color-code meaning.** Reuse a color for the same quantity across the video
  (e.g. the area term is always green, the error term always red).
- **Let things breathe.** `self.wait(0.3–1.0)` after a reveal. Don't rush.
- **Annotate, then transform.** Write a label next to a shape, then morph it into
  the next form so the viewer tracks the change.
- **Keep the frame uncluttered.** The visible canvas is roughly x ∈ [-7, 7],
  y ∈ [-4, 4]. Anything beyond that is off-screen — a frequent silent bug.

---

## Step 4 — Draft render and verify frames

Render a fast, low-res draft first:

```bash
bash scripts/render.sh examples/derivative_x2.py DerivativeOfXSquared l
# -> media/videos/<file>/480p15/<Scene>.mp4
```

Then extract sample frames and **actually look at them** — this is the single
most important quality step:

```bash
bash scripts/verify_frames.sh media/videos/derivative_x2/480p15/DerivativeOfXSquared.mp4
# writes frames/frame_*.png evenly spaced across the video; open / Read them
```

Look for: text clipped at the screen edge, labels overlapping, objects covering
each other, equations colliding with diagrams, anything off-frame. Fix in the
source, re-draft, re-check. Iterate here where renders are cheap (seconds), not
on the final pass.

`render.sh` sets `PKG_CONFIG_PATH` for Homebrew's cairo/pango so the render
doesn't fail to find them — use it rather than calling `manim` directly on macOS.

---

## Step 5 — Final render

When the draft looks right, render high quality:

```bash
bash scripts/render.sh examples/derivative_x2.py DerivativeOfXSquared h   # 1080p60
# use k for 4K (-qk). h is the right default for most uses.
```

Copy the output somewhere obvious and report the path, resolution, fps, and
duration to the user.

---

## Step 6 — Deliver and extend

Offer natural follow-ups (don't assume):

- **Vertical Short/Reel (9:16):** re-render with
  `manim -qh --resolution 1080,1920 file.py Scene`, or reframe the scene for a
  tall canvas.
- **Voiceover script:** write timed narration to read over the video.
- **GIF preview:** `ffmpeg -i out.mp4 -vf "fps=15,scale=600:-1" preview.gif` for
  README/social embeds.
- **A different topic:** suggest the next concept from `references/topic-recipes.md`.

---

## Common failure modes (read if a render breaks)

- **`FileNotFoundError: 'latex'` / "latex not found".** Something is using
  `Tex`/`MathTex`. The usual hidden culprits are `DecimalNumber`, `Integer`, and
  `Axes.get_axis_labels()`. Fix per `references/no-latex-mode.md` (use `Text`),
  or install TeX if the user wants real LaTeX.
- **`pycairo` build error / "Did not find pkg-config".** System libs missing.
  Install `pkg-config`, `cairo`, `pango` (the bootstrapper does this).
- **`always_redraw` object won't fade in/out.** Its updater overwrites opacity
  every frame. `self.add(...)` it instead of `FadeIn`, and call
  `mob.clear_updaters()` before `FadeOut`.
- **Numbers won't animate without LaTeX.** `DecimalNumber` needs LaTeX. Use a
  `Text` rebuilt each frame inside `always_redraw` (pattern in
  `references/no-latex-mode.md`).
- **Newest Python install fails (no wheels).** Recreate the venv with Python
  3.11 or 3.12.
- **Black/empty video.** A scene with no `self.play`/`self.wait`, or everything
  positioned off-canvas — verify with frames.

---

## Reference files

- `references/manim-cheatsheet.md` — core ManimCE API: mobjects, animations,
  graphing, value trackers, positioning, colors, render flags.
- `references/no-latex-mode.md` — how to make great videos with no LaTeX
  installed (and how to enable real LaTeX if wanted). **Read before writing
  equations.**
- `references/topic-recipes.md` — blueprints with skeleton code for derivatives,
  integrals/Riemann sums, the FTC, limits, the chain rule, Taylor series,
  vectors, and more.
- `examples/derivative_x2.py` — a full, working, no-LaTeX scene to learn from.
- `scripts/setup_env.sh`, `scripts/render.sh`, `scripts/verify_frames.sh` —
  environment + render + QA helpers.

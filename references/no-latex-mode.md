# Rendering math without LaTeX

Manim can render gorgeous equations with LaTeX (`MathTex`, `Tex`), but a full
TeX distribution is a multi-gigabyte install. Most machines — and most quick
jobs — don't have it. The good news: you can make excellent explainers with **no
LaTeX at all** by using Manim's Pango text engine (`Text`, `MarkupText`) plus
Unicode math symbols. This file shows how, and flags the two places a "no-LaTeX"
render still secretly invokes LaTeX and crashes.

## The rule

- **Use `Text` / `MarkupText`.** They render via Pango — no LaTeX needed.
- **Avoid `MathTex`, `Tex`, `SingleStringMathTex`.** They shell out to `latex`.
- Two innocent-looking helpers ALSO call LaTeX. Avoid them too (below).

If you forget, you get:

```
FileNotFoundError: [Errno 2] No such file or directory: 'latex'
```

## Hidden LaTeX trap #1 — DecimalNumber / Integer

`DecimalNumber`, `Integer`, and `Variable` render their digits with LaTeX. So a
"live counter" made with `DecimalNumber` crashes with no TeX installed.

**Fix — rebuild a `Text` every frame inside `always_redraw`:**

```python
a = ValueTracker(0.4)

def readout():
    xv = a.get_value()
    row1 = Text(f"x = {xv:.2f}", font_size=30, color=WHITE)
    row2 = Text(f"slope = 2x = {2*xv:.2f}", font_size=30, color=YELLOW)
    return VGroup(row1, row2).arrange(DOWN, aligned_edge=LEFT, buff=0.4).to_edge(RIGHT)

readout = always_redraw(readout)
self.add(readout)                      # add, don't FadeIn (updater overrides opacity)
self.play(a.animate.set_value(2.6), run_time=4)
# before removing it:
readout.clear_updaters()
self.play(FadeOut(readout))
```

This rebuilds the text each frame with the current value via a normal f-string —
no LaTeX, smooth live numbers. It's a little heavier than `DecimalNumber`, but
fine for the short stretches where a number animates.

## Hidden LaTeX trap #2 — Axes.get_axis_labels()

`axes.get_axis_labels(x_label="x", y_label="y")` builds the labels with
`MathTex`. Make them with `Text` instead:

```python
x_lbl = Text("x", font_size=28, color=GREY_B).next_to(axes.x_axis.get_end(), DR, buff=0.15)
y_lbl = Text("y", font_size=28, color=GREY_B).next_to(axes.y_axis.get_end(), UL, buff=0.15)
labels = VGroup(x_lbl, y_lbl)
```

(Also note: `axes.add_coordinates()` renders tick numbers with LaTeX. If you need
numbered ticks without LaTeX, place `Text` numbers manually at `axes.c2p(...)`.)

## Writing math as Unicode

Most math reads cleanly with Unicode in a normal `Text`:

| You want | Type | Unicode |
|---|---|---|
| x² , x³ | `x²` `x³` | `²` `³` |
| superscript n | `xⁿ` | `ⁿ` |
| square root | `√x` | `√` |
| integral | `∫` | `∫` |
| sum | `∑` | `∑` |
| infinity | `∞` | `∞` |
| arrow / implies | `→` `⇒` | `→` `⇒` |
| delta / partial | `Δ` `∂` | `Δ` `∂` |
| approx / ≤ ≥ ≠ | `≈ ≤ ≥ ≠` | `≈ ≤ ≥ ≠` |
| times / dot | `×` `·` | `×` `·` |
| Greek | `π θ ε λ μ σ` | … |

Define short constants at the top of the file so the code reads cleanly:

```python
SUP2, DELTA, ARROW, DOT = "²", "Δ", "→", "·"
Text(f"ΔA = 2{DOT}x{DOT}dx + dx{SUP2}", font_size=32, color=GREEN_B)
```

For fractions and richer layout, either stack with `VGroup` (numerator over a
`Line()` over denominator) or use `MarkupText` (Pango markup):

```python
MarkupText('<span size="x-large">dA</span>/<span size="x-large">dx</span> = 2x')
MarkupText('x<sup>2</sup> + <span foreground="#22c55e">2x·dx</span> + dx<sup>2</sup>')
```

`MarkupText` supports `<sup>`, `<sub>`, `<b>`, `<i>`, and per-span `foreground`
color — enough for most equation styling without LaTeX.

## When you DO want real LaTeX

If the user wants publication-grade typesetting (proper fraction bars, big
integrals, aligned multi-line derivations), install TeX and use `MathTex`:

```bash
# macOS (≈4-5 GB):
brew install --cask mactex-no-gui
#   then add TeX to PATH, e.g.:  eval "$(/usr/libexec/path_helper)"
# Debian/Ubuntu (smaller subset usually enough for Manim):
sudo apt-get install -y texlive texlive-latex-extra texlive-fonts-extra dvisvgm
```

Then:

```python
MathTex(r"\frac{d}{dx}\left[x^2\right] = 2x")
MathTex(r"\int_0^1 x^2\,dx = \tfrac{1}{3}")
```

Decide up front: **no-LaTeX (fast, portable, Unicode/Pango)** vs **LaTeX
(heavy install, crisp typesetting)**. This skill defaults to no-LaTeX because it
"just works" everywhere and looks great for the vast majority of explainers.

# ManimCE cheatsheet

Practical, copy-pasteable patterns for ManimCE (tested against Manim 0.19–0.20).
This is not the full API — it's the 20% you use 80% of the time when building
explainers. Official docs: https://docs.manim.community/

## Contents
- [Scene skeleton](#scene-skeleton)
- [Animations](#animations)
- [Common mobjects](#common-mobjects)
- [Text without LaTeX](#text-without-latex)
- [Positioning & layout](#positioning--layout)
- [Graphing with Axes](#graphing-with-axes)
- [ValueTracker + always_redraw (live updates)](#valuetracker--always_redraw-live-updates)
- [Colors](#colors)
- [Render flags](#render-flags)

---

## Scene skeleton

```python
from manim import *

class MyScene(Scene):
    def construct(self):
        self.camera.background_color = "#0e1116"
        dot = Dot()
        self.play(FadeIn(dot))
        self.wait(0.5)
```

`self.play(...)` runs animations; `self.wait(t)` holds. `self.add(m)` /
`self.remove(m)` put mobjects on screen instantly with no animation.

The visible frame is about **x ∈ [-7.1, 7.1]**, **y ∈ [-4, 4]**, origin at
center. `ORIGIN`, `UP`, `DOWN`, `LEFT`, `RIGHT`, `UL`, `UR`, `DL`, `DR` are unit
direction vectors you scale and add, e.g. `LEFT * 3 + UP * 2`.

## Animations

| Animation | Use |
|---|---|
| `Write(m)` | draw text / equations stroke by stroke |
| `Create(m)` | draw a shape's outline (lines, curves, axes) |
| `FadeIn(m, shift=UP*0.3, scale=0.8)` | appear; optional drift/scale |
| `FadeOut(m, shift=..., scale=...)` | disappear |
| `Transform(a, b)` | morph mobject `a` into the shape of `b` |
| `ReplacementTransform(a, b)` | like Transform but `b` becomes the on-screen one |
| `GrowFromEdge(m, LEFT)` | grow a shape from an edge (great for strips/bars) |
| `GrowFromCenter(m)` | grow from the middle |
| `Indicate(m, color=YELLOW, scale_factor=1.2)` | a quick attention pulse |
| `Circumscribe(m)` | flash a box/circle around something |
| `m.animate.shift(RIGHT).set_color(RED)` | animate any property change |

Run several at once by passing multiple to one `self.play(...)`. Control speed
with `run_time=` and easing with `rate_func=` (e.g. `smooth`, `linear`,
`there_and_back`, `there_and_back_with_pause`).

```python
self.play(a.animate.shift(RIGHT*2), Write(label), run_time=1.5)
```

## Common mobjects

```python
Dot(point=ORIGIN, radius=0.08, color=YELLOW)
Line(start, end, stroke_width=4, color=WHITE)
Arrow(start, end, buff=0)
Rectangle(width=3, height=2, color=BLUE, fill_color=BLUE, fill_opacity=0.5)
Square(side_length=2)
Circle(radius=1)
Polygon(p1, p2, p3)
SurroundingRectangle(mobject, color=YELLOW, buff=0.2)   # a box around something
Brace(mobject, direction=DOWN)                          # a measuring brace
VGroup(a, b, c)                                          # group; move/animate together
```

`VGroup` is the workhorse for layout — group related mobjects, then position or
animate the whole group at once.

## Text without LaTeX

This skill assumes **no LaTeX installed**. Use `Text` (Pango) with Unicode, not
`MathTex`/`Tex`. See `no-latex-mode.md` for the full story and the gotchas
(`DecimalNumber`, axis labels). Quick form:

```python
Text("slope = 2x", font_size=36, color=YELLOW, weight=BOLD)
Text("x²  →  area", font_size=40)          # Unicode ² → x²,  → arrow
MarkupText('x<sup>2</sup> + <span foreground="#3b82f6">2x</span>')   # rich markup
```

Handy Unicode: `² ³ ⁿ √ ∫ ∑ ∞ → ⇒ Δ ∂ ≈ ≤ ≥ ≠ · × π θ ε`.

## Positioning & layout

```python
b.next_to(a, RIGHT, buff=0.3)        # place b to the right of a
b.move_to(a)                          # center b on a's center
b.move_to(LEFT*3 + UP*2)              # to an absolute point
b.align_to(a, LEFT)                   # share a's left edge
b.to_edge(UP, buff=0.5)               # against the top edge
b.to_corner(UR)                       # to a corner
b.shift(DOWN*0.5)                      # nudge

VGroup(a, b, c).arrange(DOWN, aligned_edge=LEFT, buff=0.34)   # stack, left-aligned
```

**Layout tip that prevents most bugs:** build a multi-line block as one
`VGroup`, `.arrange(DOWN, aligned_edge=LEFT)`, position the *group* once with
`move_to`, then animate the children in sequence. Positioning each line
relative to the previous one tends to drift off-screen.

## Graphing with Axes

```python
axes = Axes(
    x_range=[-0.5, 3.2, 1],          # [min, max, step]
    y_range=[-0.5, 9.5, 2],
    x_length=6.5, y_length=5.2,
    axis_config={"include_tip": True, "color": GREY_B},
)
curve = axes.plot(lambda x: x**2, x_range=[-0.5, 3.05], color=BLUE_B)
point = axes.c2p(2, 4)               # coords-to-point: data (2,4) -> screen point
area  = axes.get_area(curve, x_range=[0, 2], color=GREEN, opacity=0.4)
```

**LaTeX trap:** `axes.get_axis_labels()` renders with LaTeX. Without LaTeX, make
labels yourself:

```python
x_lbl = Text("x", font_size=28).next_to(axes.x_axis.get_end(), DR, buff=0.15)
y_lbl = Text("y", font_size=28).next_to(axes.y_axis.get_end(), UL, buff=0.15)
```

## ValueTracker + always_redraw (live updates)

The pattern behind "a tangent line slides and the slope number updates live".
A `ValueTracker` holds a number you animate; `always_redraw` rebuilds a mobject
from it every frame.

```python
a = ValueTracker(0.4)

dot = always_redraw(lambda: Dot(axes.c2p(a.get_value(), a.get_value()**2), color=YELLOW))

def tangent():
    x0, s, dx = a.get_value(), 2*a.get_value(), 1.3
    return Line(axes.c2p(x0-dx, x0**2 - s*dx),
                axes.c2p(x0+dx, x0**2 + s*dx), color=YELLOW, stroke_width=4)
tangent = always_redraw(tangent)

self.add(dot, tangent)                                   # add (don't FadeIn) redrawn objects
self.play(a.animate.set_value(2.6), run_time=4, rate_func=there_and_back_with_pause)
```

**Gotchas (these bite everyone):**
- An `always_redraw` mobject's updater overwrites opacity each frame, so
  `FadeIn`/`FadeOut` on it do nothing useful. `self.add()` it; before fading it
  out, call `mob.clear_updaters()` then `FadeOut`.
- To show a number that changes without LaTeX, rebuild a `Text` inside
  `always_redraw` (see `no-latex-mode.md`) — `DecimalNumber` needs LaTeX.

## Colors

Built-ins: `BLUE BLUE_B BLUE_D TEAL GREEN GREEN_B YELLOW GOLD ORANGE RED
MAROON PURPLE PINK WHITE GREY GREY_A GREY_B BLACK`. Any hex works:
`color="#3b82f6"`. **Reuse one color per concept** across the whole video so the
viewer's eye tracks "the same thing".

## Render flags

```bash
manim -ql file.py Scene      # 480p15  draft (fast — iterate here)
manim -qm file.py Scene      # 720p30
manim -qh file.py Scene      # 1080p60 (good default for final)
manim -qk file.py Scene      # 2160p60 (4K)
manim -ql -p file.py Scene   # -p opens the player when done
manim --disable_caching ...  # force a clean re-render
manim -qh --resolution 1080,1920 file.py Scene   # vertical 9:16 (Shorts/Reels)
```

Output lands in `media/videos/<file>/<quality>/<Scene>.mp4`.

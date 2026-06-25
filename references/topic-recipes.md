# Topic recipes

Blueprints for the most-requested calculus/STEM explainers. Each recipe gives
the **core visual idea** (what carries the intuition), the **narrative beats**,
and a **skeleton** you adapt. All skeletons are no-LaTeX (Pango `Text` +
Unicode); see `no-latex-mode.md`. Start from the closest recipe instead of a
blank file.

Common header for every scene:

```python
from manim import *
SUP2, DELTA, ARROW, DOT = "²", "Δ", "→", "·"
BG = "#0e1116"
```

## Contents
1. [Derivative as the slope of a curve](#1-derivative-as-the-slope-of-a-curve)
2. [Why d/dx[x²] = 2x — the growing square](#2-why-ddxx²--2x--the-growing-square)
3. [Riemann sums → the integral](#3-riemann-sums--the-integral)
4. [The Fundamental Theorem of Calculus](#4-the-fundamental-theorem-of-calculus)
5. [Limits / epsilon–delta](#5-limits--epsilondelta)
6. [The chain rule](#6-the-chain-rule)
7. [Taylor series approximation](#7-taylor-series-approximation)
8. [Vectors & the dot product](#8-vectors--the-dot-product)

---

## 1. Derivative as the slope of a curve

**Visual:** a tangent line that slides along the curve while a live read-out
shows the slope `= f'(x)`. **Beats:** plot f → drop a point → draw the tangent →
slide it and watch the slope change → name f'(x).

```python
class SlopeOfCurve(Scene):
    def construct(self):
        self.camera.background_color = BG
        axes = Axes(x_range=[-0.5, 3.2, 1], y_range=[-0.5, 9.5, 2],
                    x_length=6.5, y_length=5.2,
                    axis_config={"include_tip": True, "color": GREY_B}).shift(LEFT*2.5)
        curve = axes.plot(lambda x: x**2, x_range=[-0.5, 3.05], color=BLUE_B)
        self.play(Create(axes), Create(curve))

        a = ValueTracker(0.4)
        dot = always_redraw(lambda: Dot(axes.c2p(a.get_value(), a.get_value()**2), color=YELLOW))
        def tangent():
            x0, s, dx = a.get_value(), 2*a.get_value(), 1.3
            return Line(axes.c2p(x0-dx, x0**2-s*dx), axes.c2p(x0+dx, x0**2+s*dx),
                        color=YELLOW, stroke_width=4)
        tan = always_redraw(tangent)
        def readout():
            xv = a.get_value()
            return VGroup(Text(f"x = {xv:.2f}", font_size=30),
                          Text(f"slope = {2*xv:.2f}", font_size=30, color=YELLOW)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).to_edge(RIGHT)
        ro = always_redraw(readout)
        self.add(dot, tan, ro)
        self.play(a.animate.set_value(2.6), run_time=4, rate_func=there_and_back_with_pause)
        self.wait()
```

Swap `x**2` (and the `2*x0` slope) for any f and its derivative.

## 2. Why d/dx[x²] = 2x — the growing square

**Visual:** `x²` as the area of a square; grow the side by `dx` and the new area
is two `x·dx` strips plus a tiny `dx²` corner. **Beats:** square = x² → grow by
dx → name the pieces → (x+dx)² = x² + 2·x·dx + dx² → divide by dx → let dx→0,
the corner vanishes → 2x. **Full worked version:** `examples/derivative_x2.py`.

Key construction (tile a big square from 4 rects):

```python
x, dx = 3.2, 0.7
bl = LEFT*5.2 + DOWN*2.6                      # bottom-left anchor
def rect(w, h, ax, ay, color):
    r = Rectangle(width=w, height=h, color=color, fill_color=color,
                  fill_opacity=0.5, stroke_width=2)
    return r.move_to(bl + RIGHT*(ax + w/2) + UP*(ay + h/2))
main   = rect(x,  x,  0, 0, BLUE)             # x²
right  = rect(dx, x,  x, 0, GREEN)            # x·dx
top    = rect(x,  dx, 0, x, GREEN)            # x·dx
corner = rect(dx, dx, x, x, RED)             # dx²
self.play(FadeIn(main))
self.play(GrowFromEdge(right, LEFT), GrowFromEdge(top, DOWN))
self.play(FadeIn(corner, scale=0.5))
# ...then write the algebra column on the right and fade out the corner as dx→0
```

## 3. Riemann sums → the integral

**Visual:** rectangles fill the area under a curve; increase their count and the
jagged sum smooths into the true area. **Beats:** plot f → draw n=4 rectangles
(visibly wrong) → animate n: 4→8→16→64 → rectangles hug the curve → "this limit
is ∫".

```python
class RiemannToIntegral(Scene):
    def construct(self):
        self.camera.background_color = BG
        axes = Axes(x_range=[0, 4, 1], y_range=[0, 9, 2], x_length=7, y_length=5,
                    axis_config={"color": GREY_B}).shift(DOWN*0.3)
        f = lambda x: 0.4*x**2 + 0.5
        curve = axes.plot(f, x_range=[0, 4], color=BLUE_B)
        self.play(Create(axes), Create(curve))

        def rects(n):
            return axes.get_riemann_rectangles(curve, x_range=[0, 4], dx=4/n,
                       input_sample_type="right", stroke_width=0.5,
                       fill_opacity=0.7, color=(TEAL, GREEN))
        r = rects(4)
        self.play(Create(r))
        for n in (8, 16, 32, 64):
            self.play(Transform(r, rects(n)), run_time=1.2)
            self.add(Text(f"n = {n}", font_size=30).to_corner(UR))   # or update one label
        area = axes.get_area(curve, x_range=[0, 4], color=GREEN, opacity=0.5)
        self.play(FadeIn(area))
        self.play(Write(Text("∫ f(x) dx  =  area", font_size=40, color=GREEN).to_edge(UP)))
        self.wait()
```

(For a clean count label, make one `Text`/`always_redraw` driven by a tracker
rather than stacking new labels.)

## 4. The Fundamental Theorem of Calculus

**Visual:** a moving right-edge sweeps out the area `A(x)` under f; the *rate*
that area grows equals the *height* f(x). **Beats:** show f → shade area up to a
moving x → plot A(x) on a second axis → "the slope of A is f" → A'(x)=f(x).

```python
class FTC(Scene):
    def construct(self):
        self.camera.background_color = BG
        ax = Axes(x_range=[0,4,1], y_range=[0,5,1], x_length=6, y_length=3.2).to_edge(UP)
        f = lambda x: 1 + 0.6*x
        curve = ax.plot(f, color=BLUE_B)
        t = ValueTracker(0.3)
        area = always_redraw(lambda: ax.get_area(curve, x_range=[0, t.get_value()],
                                                  color=GREEN, opacity=0.5))
        self.play(Create(ax), Create(curve)); self.add(area)
        # second axes for A(x); plot accumulated area as t moves
        ax2 = Axes(x_range=[0,4,1], y_range=[0,12,3], x_length=6, y_length=3.2).to_edge(DOWN)
        A = lambda x: x + 0.3*x**2                # ∫(1+0.6x)dx
        Acurve = always_redraw(lambda: ax2.plot(A, x_range=[0, t.get_value()], color=GREEN))
        self.play(Create(ax2)); self.add(Acurve)
        self.play(t.animate.set_value(3.7), run_time=5)
        self.play(Write(Text("A'(x) = f(x)", font_size=40, color=YELLOW).to_corner(UR)))
```

## 5. Limits / epsilon–delta

**Visual:** a horizontal ε-band around L and a vertical δ-band around c; shrink ε
and show you can always find a δ that keeps the graph inside the box. **Beats:**
plot f near c → draw the ε band → "can we trap the output?" → draw δ → shrink ε,
δ follows → that's the limit.

```python
class EpsilonDelta(Scene):
    def construct(self):
        self.camera.background_color = BG
        ax = Axes(x_range=[-1, 3, 1], y_range=[-1, 5, 1], x_length=7, y_length=5)
        f = lambda x: x + 1
        curve = ax.plot(f, color=BLUE_B); c, L = 1.5, 2.5
        self.play(Create(ax), Create(curve))
        eps = ValueTracker(1.2)
        band = always_redraw(lambda: Rectangle(
            width=ax.x_length, height=2*eps.get_value()*ax.y_axis.unit_size,
            color=YELLOW, fill_opacity=0.15, stroke_width=1).move_to(ax.c2p(1, L)))
        self.add(band)
        for e in (0.8, 0.5, 0.25):
            self.play(eps.animate.set_value(e), run_time=1.2)
        self.play(Write(Text(f"lim f(x) = {L}", font_size=40, color=YELLOW).to_edge(UP)))
```

## 6. The chain rule

**Visual:** two coupled number lines (or dials) — turning `x` turns `u=g(x)`,
which turns `y=f(u)`; total sensitivity multiplies. **Beats:** x→u with rate
g'(x) → u→y with rate f'(u) → chain them → dy/dx = f'(g(x))·g'(x).

```python
class ChainRule(Scene):
    def construct(self):
        self.camera.background_color = BG
        nl_x = NumberLine(x_range=[0,3,1], length=5).to_edge(UP)
        nl_u = NumberLine(x_range=[0,9,3], length=5)
        nl_y = NumberLine(x_range=[0,9,3], length=5).to_edge(DOWN)
        for nl, name in [(nl_x,"x"), (nl_u,"u = g(x)"), (nl_y,"y = f(u)")]:
            self.play(Create(nl), Write(Text(name, font_size=28).next_to(nl, LEFT)))
        t = ValueTracker(0.4)
        g, f = (lambda x: x**2), (lambda u: u)        # u=x², y=u
        dx = always_redraw(lambda: Dot(nl_x.n2p(t.get_value()), color=YELLOW))
        du = always_redraw(lambda: Dot(nl_u.n2p(g(t.get_value())), color=GREEN))
        dy = always_redraw(lambda: Dot(nl_y.n2p(f(g(t.get_value()))), color=RED))
        self.add(dx, du, dy)
        self.play(t.animate.set_value(2.5), run_time=4)
        self.play(Write(Text("dy/dx = f'(g(x))·g'(x)", font_size=36, color=YELLOW)))
```

## 7. Taylor series approximation

**Visual:** start with the constant term and watch each added polynomial term
hug the true curve over a wider interval. **Beats:** plot f (e.g. cos) → overlay
degree-0, then 2, 4, 6 partial sums → each clings to f further out.

```python
import math
class TaylorCosine(Scene):
    def construct(self):
        self.camera.background_color = BG
        ax = Axes(x_range=[-PI, PI, 1], y_range=[-2, 2, 1], x_length=9, y_length=4.5)
        true = ax.plot(lambda x: math.cos(x), color=BLUE_B)
        self.play(Create(ax), Create(true))
        def taylor(n):                                   # partial sum of cos
            terms = [( (-1)**k )/math.factorial(2*k) for k in range(n+1)]
            return ax.plot(lambda x: sum(c*x**(2*k) for k,c in enumerate(terms)),
                           x_range=[-PI, PI], color=YELLOW)
        approx = taylor(0); self.play(Create(approx))
        for n in (1,2,3,4):
            self.play(Transform(approx, taylor(n)), run_time=1.2)
        self.wait()
```

## 8. Vectors & the dot product

**Visual:** two arrows from the origin; the dot product = (length of one) × (the
other's shadow onto it). **Beats:** draw a, b → draw the projection of b onto a →
a·b = |a|·proj → rotate b, watch the sign flip at 90°.

```python
class DotProduct(Scene):
    def construct(self):
        self.camera.background_color = BG
        plane = NumberPlane(x_range=[-5,5], y_range=[-3,3]).set_opacity(0.3)
        a = Arrow(ORIGIN, [3,1,0], buff=0, color=BLUE)
        b = Arrow(ORIGIN, [1,2,0], buff=0, color=YELLOW)
        self.play(Create(plane), GrowArrow(a), GrowArrow(b))
        # projection of b onto a:
        import numpy as np
        av, bv = np.array([3,1,0]), np.array([1,2,0])
        proj = (av @ bv)/(av @ av) * av
        proj_arrow = Arrow(ORIGIN, proj, buff=0, color=GREEN)
        self.play(GrowArrow(proj_arrow))
        self.play(Write(Text("a · b = |a| × (shadow of b)", font_size=34).to_edge(UP)))
```

---

### Adapting any recipe

1. Replace the function(s) and their derivatives/integrals.
2. Re-pick `x_range`/`y_range` so the interesting part fills the frame.
3. Keep one color per quantity; reuse it across beats.
4. Draft-render `-ql`, run `verify_frames.sh`, fix layout, then final `-qh`.

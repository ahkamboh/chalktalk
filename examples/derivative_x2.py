"""
Why is the derivative of x^2 equal to 2x?

A 3Blue1Brown-style explainer rendered with ManimCE.

This file avoids Tex/MathTex (no LaTeX installed) and uses Pango `Text`
with Unicode math symbols instead.

Render:
    manim -qh derivative_x2.py DerivativeOfXSquared
"""

from manim import *

# Unicode helpers
SUP2 = "²"        # superscript 2  -> x²
DELTA = "Δ"       # Δ
ARROW = "→"       # →
DOT = "·"         # ·  (multiplication dot)

BG = "#0e1116"


class DerivativeOfXSquared(Scene):
    def construct(self):
        self.camera.background_color = BG

        self.part1_title()
        self.part2_slope_of_parabola()
        self.part3_geometric_proof()
        self.part4_conclusion()

    # ------------------------------------------------------------------ #
    def part1_title(self):
        q = Text("What is the derivative of", font_size=40, color=GREY_A)
        f = Text(f"f(x) = x{SUP2}", font_size=72, color=BLUE_B, weight=BOLD)
        sub = Text("?", font_size=72, color=YELLOW)
        f.next_to(q, DOWN, buff=0.4)
        sub.next_to(f, RIGHT, buff=0.15).align_to(f, DOWN)
        group = VGroup(q, f).move_to(ORIGIN)

        self.play(FadeIn(q, shift=UP * 0.3))
        self.play(Write(f))
        self.wait(0.8)
        ans = Text(f"d/dx [ x{SUP2} ] = 2x", font_size=56, color=YELLOW, weight=BOLD)
        ans.next_to(group, DOWN, buff=0.7)
        self.play(FadeIn(ans, shift=UP * 0.3))
        self.wait(1.0)
        self.play(FadeOut(VGroup(group, ans)))

    # ------------------------------------------------------------------ #
    def part2_slope_of_parabola(self):
        header = Text("It's the slope of the curve at each point",
                      font_size=30, color=GREY_A).to_edge(UP, buff=0.5)
        self.play(FadeIn(header))

        axes = Axes(
            x_range=[-0.5, 3.2, 1],
            y_range=[-0.5, 9.5, 2],
            x_length=6.5,
            y_length=5.2,
            axis_config={"include_tip": True, "color": GREY_B},
            tips=True,
        ).to_edge(DOWN, buff=0.6).shift(LEFT * 2.5)

        x_axis_lbl = Text("x", font_size=28, color=GREY_B).next_to(
            axes.x_axis.get_end(), DR, buff=0.15)
        y_axis_lbl = Text("y", font_size=28, color=GREY_B).next_to(
            axes.y_axis.get_end(), UL, buff=0.15)
        labels = VGroup(x_axis_lbl, y_axis_lbl)
        curve = axes.plot(lambda x: x ** 2, x_range=[-0.5, 3.05], color=BLUE_B)
        curve_lbl = Text(f"y = x{SUP2}", font_size=30, color=BLUE_B)
        curve_lbl.next_to(axes.c2p(2.6, 6.8), UR, buff=0.05)

        self.play(Create(axes), FadeIn(labels))
        self.play(Create(curve), Write(curve_lbl))
        self.wait(0.3)

        a = ValueTracker(0.4)

        def get_point():
            return axes.c2p(a.get_value(), a.get_value() ** 2)

        dot = always_redraw(lambda: Dot(get_point(), color=YELLOW, radius=0.08))

        def tangent_line():
            x0 = a.get_value()
            slope = 2 * x0
            dx = 1.3
            p1 = axes.c2p(x0 - dx, (x0 ** 2) - slope * dx)
            p2 = axes.c2p(x0 + dx, (x0 ** 2) + slope * dx)
            return Line(p1, p2, color=YELLOW, stroke_width=4)

        tangent = always_redraw(tangent_line)

        # Live read-out panel on the right (Text-based, no LaTeX)
        def make_readout():
            xv = a.get_value()
            row1 = Text(f"at  x = {xv:.2f}", font_size=30, color=WHITE)
            row2 = Text(f"slope = 2x = {2 * xv:.2f}", font_size=30, color=YELLOW)
            g = VGroup(row1, row2).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
            return g.to_edge(RIGHT, buff=0.7).shift(UP * 0.3)

        readout = always_redraw(make_readout)

        self.play(Create(tangent), FadeIn(dot))
        self.add(readout)
        self.wait(0.3)
        self.play(a.animate.set_value(2.6), run_time=4, rate_func=there_and_back_with_pause)
        self.wait(0.3)
        self.play(a.animate.set_value(1.5), run_time=1.5)
        self.wait(0.5)

        readout.clear_updaters()
        self.play(
            FadeOut(VGroup(axes, labels, curve, curve_lbl, dot, tangent,
                           readout, header))
        )

    # ------------------------------------------------------------------ #
    def part3_geometric_proof(self):
        header = Text(f"Proof:  think of x{SUP2} as the area of a square",
                      font_size=30, color=GREY_A).to_edge(UP, buff=0.5)
        self.play(FadeIn(header))

        # geometry: a square of side x, grown by a sliver dx
        x = 3.2
        dx = 0.7
        bl = LEFT * 5.2 + DOWN * 2.6   # bottom-left anchor of the big square

        def rect(w, h, anchor_x, anchor_y, color, fill=0.5):
            r = Rectangle(width=w, height=h, color=color,
                          fill_color=color, fill_opacity=fill, stroke_width=2)
            r.move_to(bl + RIGHT * (anchor_x + w / 2) + UP * (anchor_y + h / 2))
            return r

        main = rect(x, x, 0, 0, BLUE)            # x · x  = x²
        right = rect(dx, x, x, 0, GREEN)         # dx · x
        top = rect(x, dx, 0, x, GREEN)           # x · dx
        corner = rect(dx, dx, x, x, RED)         # dx · dx

        x_lbl_b = Text("x", font_size=30, color=BLUE_B).next_to(main, DOWN, buff=0.15)
        x_lbl_l = Text("x", font_size=30, color=BLUE_B).next_to(main, LEFT, buff=0.15)
        area_main = Text(f"x{SUP2}", font_size=44, color=WHITE).move_to(main)

        # Build the original square
        self.play(FadeIn(main), Write(x_lbl_b), Write(x_lbl_l))
        self.play(Write(area_main))
        self.wait(0.4)

        # Grow it by dx
        grow_lbl = Text(f"now grow x by a tiny step  dx", font_size=26, color=GREY_A)
        grow_lbl.next_to(header, DOWN, buff=0.35)
        self.play(FadeIn(grow_lbl))

        self.play(GrowFromEdge(right, LEFT), GrowFromEdge(top, DOWN), run_time=1.2)
        self.play(FadeIn(corner, scale=0.5))

        dx_b = Text("dx", font_size=22, color=GREEN_B).next_to(corner, UP, buff=0.1)
        dx_l = Text("dx", font_size=22, color=GREEN_B).next_to(right, RIGHT, buff=0.12)
        self.play(FadeIn(dx_b), FadeIn(dx_l))
        self.wait(0.3)

        a_right = Text(f"x{DOT}dx", font_size=22, color=BLACK).move_to(right)
        a_top = Text(f"x{DOT}dx", font_size=22, color=BLACK).move_to(top)
        a_corner = Text(f"dx{SUP2}", font_size=16, color=WHITE).move_to(corner)
        self.play(Write(a_right), Write(a_top), FadeIn(a_corner))
        self.wait(0.6)
        self.play(FadeOut(grow_lbl))

        # Right-hand equation column: pre-arranged, left-aligned, guaranteed to fit
        eq1 = Text(f"(x + dx){SUP2}", font_size=32, color=WHITE)
        eq2 = Text(f"=  x{SUP2} + 2{DOT}x{DOT}dx + dx{SUP2}", font_size=32, color=WHITE)
        dA = Text(f"{DELTA}A  =  2{DOT}x{DOT}dx + dx{SUP2}", font_size=32, color=GREEN_B)
        divide = Text(f"{DELTA}A / dx  =  2x + dx", font_size=32, color=YELLOW)
        limit = Text(f"let dx {ARROW} 0,  drop dx{SUP2}", font_size=26, color=GREY_A)
        result = Text("dA/dx  =  2x", font_size=40, color=YELLOW, weight=BOLD)

        column = VGroup(eq1, eq2, dA, divide, limit, result)\
            .arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        column.move_to(RIGHT * 3.4 + UP * 0.1)
        box = SurroundingRectangle(result, color=YELLOW, buff=0.18)

        self.play(Write(eq1))
        self.play(Write(eq2))
        self.wait(0.4)
        self.play(Write(dA))
        self.wait(0.3)
        self.play(Write(divide))
        self.wait(0.4)
        self.play(FadeIn(limit))
        self.play(Indicate(corner, color=RED, scale_factor=1.3),
                  Indicate(a_corner, color=RED))
        self.play(FadeOut(corner, scale=0.1), FadeOut(a_corner, scale=0.1))
        self.wait(0.3)
        self.play(Write(result), Create(box))
        self.wait(1.2)

        self.geo_group = VGroup(
            header, main, right, top, corner, x_lbl_b, x_lbl_l, area_main,
            dx_b, dx_l, a_right, a_top, a_corner,
            column, box
        )

    # ------------------------------------------------------------------ #
    def part4_conclusion(self):
        self.play(FadeOut(self.geo_group))
        final = Text(f"d/dx [ x{SUP2} ] = 2x", font_size=72, color=YELLOW, weight=BOLD)
        tag = Text("the rate of growth of area  =  the perimeter that's moving",
                   font_size=26, color=GREY_A)
        tag.next_to(final, DOWN, buff=0.6)
        self.play(Write(final))
        self.play(FadeIn(tag, shift=UP * 0.3))
        self.wait(1.5)
        self.play(FadeOut(VGroup(final, tag)))
        self.wait(0.5)

# -*- coding: utf-8 -*-
"""Weight synthesis for non-interpolatable CJK masters.

Apple ships PingFang SC as six hand-finished static faces whose outlines are not
point compatible, so they cannot feed varLib directly.  PingFang Regular (400)
is kept as the canonical *topology*; every other weight is produced by a miter
outline offset along the point normals.

Two safeguards make the offset usable on CJK:

* the offset distance of a glyph is solved against the ink area of the genuine
  PingFang master of that weight (so the weight ramp is Apple's, not ours), and
* every point carries a collision limit derived from its distance to the nearest
  foreign boundary (a counter on the other side of a stroke, the opposite side of
  a thin bar, ...).  Displacements are clamped to that limit, which prevents the
  classic offsetting failure modes - collapsed hairlines and filled-in counters.
"""
import math
import numpy as np
from fontTools.pens.areaPen import AreaPen
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.pens.perimeterPen import PerimeterPen

MAX_MITER = 4.0
CLEARANCE = 0.45      # fraction of the free half-width a point may travel
NEIGHBOUR_SKIP = 12   # contour-index distance ignored in the collision search


def _perp(tx, ty, sign):
    # sign=+1 for clockwise (TrueType outer) contours, -1 for holes
    return (-ty * sign, tx * sign)


def _norm(x, y):
    d = math.hypot(x, y)
    if d < 1e-9:
        return (0.0, 0.0)
    return (x / d, y / d)


def _contour_area(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        a += x0 * y1 - x1 * y0
    return a * 0.5


def _contour_normals(points, flags):
    """Outward-pointing unit normals (miter corrected) for every point."""
    n = len(points)
    ons = [i for i in range(n) if flags[i]]
    if not ons:
        return None
    sign = 1.0 if _contour_area(points) < 0 else -1.0  # TrueType outer = clockwise

    def prev_on(i):
        j = (i - 1) % n
        while not flags[j]:
            j = (j - 1) % n
        return j

    def next_on(i):
        j = (i + 1) % n
        while not flags[j]:
            j = (j + 1) % n
        return j

    dirs = [(0.0, 0.0)] * n
    for i in ons:
        p = points[i]
        p_in = points[(i - 1) % n]
        p_out = points[(i + 1) % n]
        t_in = _norm(p[0] - p_in[0], p[1] - p_in[1])
        t_out = _norm(p_out[0] - p[0], p_out[1] - p[1])
        if t_in == (0.0, 0.0):
            t_in = t_out
        if t_out == (0.0, 0.0):
            t_out = t_in
        n_in = _perp(t_in[0], t_in[1], sign)
        n_out = _perp(t_out[0], t_out[1], sign)
        dot = n_in[0] * n_out[0] + n_in[1] * n_out[1]
        if dot > 0.9999:
            dirs[i] = n_out
        else:
            s = 1.0 + dot
            if s < 1.0 / MAX_MITER:
                s = 1.0 / MAX_MITER
            dirs[i] = ((n_in[0] + n_out[0]) / s, (n_in[1] + n_out[1]) / s)
    for i in range(n):
        if flags[i]:
            continue
        a = prev_on(i)
        b = next_on(i)
        t = _norm(points[b][0] - points[a][0], points[b][1] - points[a][1])
        if t == (0.0, 0.0):
            t = (1.0, 0.0)
        nn = _perp(t[0], t[1], sign)
        dirs[i] = (2.0 * nn[0], 2.0 * nn[1])  # quadratic: control = 2x midpoint
    return dirs


def collision_limits(points, contour_ids, contour_lens):
    """Per-point maximum travel distance before hitting another boundary.

    A point may travel at most CLEARANCE of the way to the nearest foreign
    boundary (a counter across a stroke, the far side of a thin bar, the
    neighbouring stroke of the same radical, ...).  Points of the same contour
    are only considered once they are far enough apart along the ring, so that
    ordinary neighbouring points never block each other.
    """
    n = len(points)
    if n < 2:
        return np.full(n, np.inf)
    # per-contour ring skip threshold
    thr = np.array([max(1, min(NEIGHBOUR_SKIP, contour_lens[cid] // 3))
                    for cid in contour_ids])
    lim = np.full(n, np.inf)
    chunk = 800
    ring_all = np.minimum(np.abs(np.arange(n)[:, None] - np.arange(n)[None, :]),
                          n - np.abs(np.arange(n)[:, None] - np.arange(n)[None, :]))
    for s in range(0, n, chunk):
        e = min(s + chunk, n)
        d = np.linalg.norm(points[s:e, None, :] - points[None, :, :], axis=2)
        same = contour_ids[s:e][:, None] == contour_ids[None, :]
        blocked = same & (ring_all[s:e] <= thr[s:e][:, None])
        d = np.where(blocked, np.inf, d)
        lim[s:e] = d.min(axis=1)
    return lim * CLEARANCE


def _ink_inside(pt, polys):
    """Even-odd point-in-glyph test against flattened contour polygons."""
    x, y = pt
    inside = False
    for poly in polys:
        x0 = poly[:, 0]
        y0 = poly[:, 1]
        x1 = np.roll(x0, -1)
        y1 = np.roll(y0, -1)
        cond = ((y0 <= y) & (y1 > y)) | ((y1 <= y) & (y0 > y))
        if not cond.any():
            continue
        xs = x0[cond] + (y - y0[cond]) / (y1[cond] - y0[cond]) * (x1[cond] - x0[cond])
        if (xs > x).sum() % 2:
            inside = not inside
    return inside


class GlyphGeometry:
    __slots__ = ("points", "normals", "limits", "contour_ranges")

    def __init__(self, points, normals, limits, contour_ranges):
        self.points = points
        self.normals = normals
        self.limits = limits
        self.contour_ranges = contour_ranges


def glyph_geometry(glyph):
    """Normals pointing out of the ink for every on/off curve point.

    TrueType only *recommends* a winding direction and PingFang mixes both, so
    each contour is oriented empirically: we hop a few units along the computed
    normal and ask the even-odd filling rule whether we landed inside the glyph.
    """
    if glyph.numberOfContours <= 0:
        return None
    pts = [(float(x), float(y)) for x, y in glyph.coordinates]
    flags = [bool(f & 1) for f in glyph.flags]
    normals = [(0.0, 0.0)] * len(pts)
    ids = [0] * len(pts)
    ranges = []
    start = 0
    for end in glyph.endPtsOfContours:
        ranges.append((start, end + 1))
        start = end + 1
    P = np.array(pts, dtype=float)
    polys = [P[s:e] for s, e in ranges]
    for ci, (s, e) in enumerate(ranges):
        dirs = _contour_normals(pts[s:e], flags[s:e])
        if dirs is None:
            return None
        # orient: normal must leave the ink
        probes = [k for k in range(e - s) if flags[s + k]][:6]
        votes = 0
        for k in probes:
            d = dirs[k]
            m = math.hypot(d[0], d[1])
            if m < 1e-9:
                continue
            u = (d[0] / m * 3.0, d[1] / m * 3.0)
            p = pts[s + k]
            if _ink_inside((p[0] + u[0], p[1] + u[1]), polys):
                votes += 1
            elif _ink_inside((p[0] - u[0], p[1] - u[1]), polys):
                votes -= 1
        flip = -1.0 if votes > 0 else 1.0
        for k, d in enumerate(dirs):
            normals[s + k] = (d[0] * flip, d[1] * flip)
            ids[s + k] = ci
    N = np.array(normals, dtype=float)
    ids = np.array(ids)
    lens = [e - s for s, e in ranges]
    limits = collision_limits(P, ids, lens)
    return GlyphGeometry(P, N, limits, ranges)


def offset_points(geo, dist):
    """Displaced coordinates for a single offset distance."""
    disp = geo.normals * dist
    mag = np.hypot(disp[:, 0], disp[:, 1])
    lim = geo.limits
    over = mag > lim
    if over.any():
        scale = np.ones_like(mag)
        scale[over] = lim[over] / mag[over]
        disp = disp * scale[:, None]
    return geo.points + disp


def glyph_area(glyphset, name):
    pen = AreaPen(glyphset)
    glyphset[name].draw(pen)
    return abs(pen.value)


def glyph_perimeter(glyphset, name):
    pen = PerimeterPen(glyphset)
    glyphset[name].draw(pen)
    return pen.value


def measure(font):
    """Ink area and perimeter for every glyph of a font."""
    gs = font.getGlyphSet()
    out = {}
    for name in font.getGlyphOrder():
        try:
            out[name] = (glyph_area(gs, name), glyph_perimeter(gs, name))
        except Exception:
            out[name] = (0.0, 0.0)
    return out


def solve_distance(a0, p0, a_target):
    """First guess of the offset distance from the linear area model."""
    if p0 <= 0 or a0 <= 0:
        return 0.0
    m = (a_target - a0) / p0
    span = a0 / p0
    lo, hi = -0.9 * span, 2.2 * span
    return max(lo, min(hi, m))


class WeightSynthesizer:
    """Turns the Regular CJK master into any other weight, glyph by glyph."""

    def __init__(self, base_font, base_measure):
        self.base_measure = base_measure
        self.glyf = base_font["glyf"]
        self.geos = {}
        self.components = {}
        for name in base_font.getGlyphOrder():
            g = self.glyf[name]
            if g.numberOfContours < 0:
                self.components[name] = tuple(
                    (c.glyphName, math.hypot(c.transform[0][0], c.transform[1][0]) or 1.0)
                    for c in g.components)
            else:
                self.geos[name] = glyph_geometry(g)

    def distance(self, name, target_area):
        a0, p0 = self.base_measure.get(name, (0.0, 0.0))
        if a0 <= 0 or p0 <= 0:
            return 0.0
        return solve_distance(a0, p0, target_area)

    def apply(self, name, dist, glyf):
        geo = self.geos.get(name)
        if geo is None or not dist:
            return False
        out = offset_points(geo, dist)
        g = glyf[name]
        g.coordinates = GlyphCoordinates(out)
        g.recalcBounds(glyf)
        return True

    def build_distances(self, dist, out_font):
        """Displace every glyph by its own solved distance."""
        glyf = out_font["glyf"]
        done = set()
        for name in out_font.getGlyphOrder():
            if name in self.components:
                continue
            d = dist.get(name, 0.0)
            if d:
                self.apply(name, d, glyf)
        for name in out_font.getGlyphOrder():
            comps = self.components.get(name)
            if not comps:
                continue
            g = glyf[name]
            for idx, c in enumerate(g.components):
                if c.glyphName in done:
                    continue
                done.add(c.glyphName)
                child_scale = comps[idx][1]
                d = dist.get(c.glyphName, 0.0)
                if not d:
                    continue
                self.apply(c.glyphName, d / max(child_scale, 1e-6), glyf)
        return out_font

    def build(self, target_areas, out_font):
        dist = {n: self.distance(n, target_areas.get(n, 0.0))
                for n in out_font.getGlyphOrder()}
        return self.build_distances(dist, out_font)

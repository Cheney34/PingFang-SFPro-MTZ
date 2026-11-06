# -*- coding: utf-8 -*-
"""Tiny scanline rasteriser used to validate synthetic weights against the
genuine PingFang masters (no external dependencies besides numpy)."""
import numpy as np
from fontTools.pens.basePen import BasePen


class PolyPen(BasePen):
    """Flattens a glyph outline into closed polygons (font units)."""

    def __init__(self, glyphSet, steps=6):
        super().__init__(glyphSet)
        self.steps = steps
        self.polys = []
        self._cur = None

    def _moveTo(self, pt):
        self._cur = [pt]

    def _lineTo(self, pt):
        self._cur.append(pt)

    def _curveToOne(self, p1, p2, p3):
        p0 = np.array(self._cur[-1], dtype=float)
        p1, p2, p3 = (np.array(p, dtype=float) for p in (p1, p2, p3))
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1 - t
            self._cur.append(tuple(mt**3 * p0 + 3 * mt**2 * t * p1 + 3 * mt * t**2 * p2 + t**3 * p3))

    def _qCurveToOne(self, p1, p2):
        p0 = np.array(self._cur[-1], dtype=float)
        p1, p2 = np.array(p1, dtype=float), np.array(p2, dtype=float)
        for i in range(1, self.steps + 1):
            t = i / self.steps
            mt = 1 - t
            self._cur.append(tuple(mt**2 * p0 + 2 * mt * t * p1 + t**2 * p2))

    def _closePath(self):
        if self._cur and len(self._cur) > 2:
            self.polys.append(np.array(self._cur, dtype=float))
        self._cur = None

    def _endPath(self):
        self._closePath()


def polygons(glyphset, name, steps=6):
    pen = PolyPen(glyphset, steps)
    glyphset[name].draw(pen)
    return pen.polys


def raster(polys, size=160, pad=0.08):
    """Even-odd scanline fill; returns (mask, transform) in a size x size box."""
    if not polys:
        return np.zeros((size, size), dtype=bool), None
    allpts = np.vstack(polys)
    xmin, ymin = allpts.min(axis=0)
    xmax, ymax = allpts.max(axis=0)
    w, h = max(xmax - xmin, 1.0), max(ymax - ymin, 1.0)
    scale = (size * (1 - 2 * pad)) / max(w, h)
    ox = (size - w * scale) / 2 - xmin * scale
    oy = (size - h * scale) / 2 - ymin * scale
    mask = np.zeros((size, size), dtype=bool)
    rows = np.arange(size) + 0.5
    for poly in polys:
        p = poly * scale
        p[:, 0] += ox
        p[:, 1] += oy
        y0 = p[:, 1]
        y1 = np.roll(p[:, 1], -1)
        x0 = p[:, 0]
        x1 = np.roll(p[:, 0], -1)
        for r in range(size):
            yc = rows[r]
            cond = ((y0 <= yc) & (y1 > yc)) | ((y1 <= yc) & (y0 > yc))
            if not cond.any():
                continue
            xs = x0[cond] + (yc - y0[cond]) / (y1[cond] - y0[cond]) * (x1[cond] - x0[cond])
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                a = int(np.ceil(xs[i] - 0.5))
                b = int(np.floor(xs[i + 1] - 0.5))
                if b >= a:
                    mask[r, max(a, 0):min(b + 1, size)] ^= True
    return mask, scale


def iou(a, b):
    inter = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    return float(inter) / float(union) if union else 1.0


def raster_box(polys, box, size=160, pad=0.06):
    """Even-odd scanline fill of polys into a fixed font-unit box."""
    mask = np.zeros((size, size), dtype=bool)
    if not polys:
        return mask
    xmin, ymin, xmax, ymax = box
    w, h = max(xmax - xmin, 1.0), max(ymax - ymin, 1.0)
    scale = (size * (1 - 2 * pad)) / max(w, h)
    ox = (size - w * scale) / 2 - xmin * scale
    oy = (size - h * scale) / 2 - ymin * scale
    rows = np.arange(size) + 0.5
    for poly in polys:
        p = poly * scale
        p[:, 0] += ox
        p[:, 1] += oy
        y0 = p[:, 1]
        y1 = np.roll(p[:, 1], -1)
        x0 = p[:, 0]
        x1 = np.roll(p[:, 0], -1)
        for rr in range(size):
            yc = rows[rr]
            cond = ((y0 <= yc) & (y1 > yc)) | ((y1 <= yc) & (y0 > yc))
            if not cond.any():
                continue
            xs = x0[cond] + (yc - y0[cond]) / (y1[cond] - y0[cond]) * (x1[cond] - x0[cond])
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                a = int(np.ceil(xs[i] - 0.5))
                b = int(np.floor(xs[i + 1] - 0.5))
                if b >= a:
                    mask[rr, max(a, 0):min(b + 1, size)] ^= True
    return mask

# -*- coding: utf-8 -*-
"""Stage 4: build the seven synthetic CJK masters (wght 100..700).

PingFang Regular (400) supplies the canonical topology.  Every other weight is
produced by a collision-clamped miter offset whose per-glyph distance is solved
against the ink area of the genuine PingFang master of that weight and then
refined with Newton steps against the measured result.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from lib.synth import WeightSynthesizer, measure, solve_distance
from fontTools.ttLib import TTFont

PASSES = 5
TOL = 0.02


def target_areas_for(w, pf_fonts, cache):
    if w in cache:
        return cache[w]
    if w == 700:                      # no genuine 700: extrapolate from 500/600
        a5 = target_areas_for(500, pf_fonts, cache)
        a6 = target_areas_for(600, pf_fonts, cache)
        out = {}
        for name, (a, p) in a6.items():
            a5v = a5.get(name, (a, p))[0]
            out[name] = (a + (a - a5v) * 0.9, p)
        cache[700] = out
        return out
    out = measure(pf_fonts[w])
    cache[w] = out
    return out


def refine(base_path, base_measure, synth, targets, out_path):
    dist = {n: synth.distance(n, targets.get(n, (0.0, 0.0))[0])
            for n in base_measure}
    worst = 1.0
    for p in range(PASSES):
        font = TTFont(base_path)
        synth.build_distances(dist, font)
        got = measure(font)
        worst, worst_name = 0.0, ""
        for n, d in list(dist.items()):
            ta = targets.get(n, (0.0, 0.0))[0]
            ga, gp = got.get(n, (0.0, 0.0))
            if ta <= 0 or ga <= 0 or gp <= 0:
                continue
            err = (ta - ga) / ta
            if abs(err) > worst:
                worst, worst_name = abs(err), n
            dist[n] = d + max(-40.0, min(40.0, (ta - ga) / gp))
        log(f"    pass {p}: worst area error {worst*100:5.1f}% ({worst_name or '-'})")
        if worst < TOL:
            break
    font = TTFont(base_path)
    synth.build_distances(dist, font)
    font.save(out_path)
    return font


def main():
    ensure_dirs()
    t0 = time.time()
    base_path = os.path.join(WORK, "pf", "pf-400.ttf")
    base = TTFont(base_path)
    base_measure = measure(base)
    synth = WeightSynthesizer(base, base_measure)
    log(f"[base] {len(synth.geos)} simple, {len(synth.components)} composite glyphs, "
        f"{time.time()-t0:.1f}s")

    pf_fonts = {w: TTFont(os.path.join(WORK, "pf", f"pf-{w}.ttf"))
                for _, w in PF_WEIGHTS}
    cache = {}
    for w in SYNTH_WEIGHTS:
        if w == 400:
            out = os.path.join(WORK, "masters", f"cjk-{w}.ttf")
            import shutil
            shutil.copyfile(base_path, out)
            log(f"[cjk] wght {w}: copy of PingFang Regular")
            continue
        t1 = time.time()
        targets = target_areas_for(w, pf_fonts, cache)
        out = os.path.join(WORK, "masters", f"cjk-{w}.ttf")
        refine(base_path, base_measure, synth, targets, out)
        log(f"[cjk] wght {w}: {os.path.getsize(out)//1024} KiB ({time.time()-t1:.1f}s)")
    log(f"done in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

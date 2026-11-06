# -*- coding: utf-8 -*-
"""Stage 2: prepare per-weight static sources.

 * SF Pro (variable, wght 1-1000, opsz 17-28) -> one static instance per weight,
   rescaled from 2048 to 1000 upem and subset to the Latin/Greek/Cyrillic/symbol
   codepoints that the theme takes from SF Pro.
 * PingFang SC (6 static weights, upem 1000) -> subset to the *complement* of the
   SF Pro codepoint set, so that every master shares one identical glyph set.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools import subset

def subset_to_codepoints(font, cps, layout_features="*", keep_gvar=False):
    opts = subset.Options()
    opts.layout_features = [layout_features] if layout_features != "*" else ["*"]
    opts.name_IDs = ["*"]
    opts.name_legacy = True
    opts.name_languages = ["*"]
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.recalc_timestamp = False
    opts.drop_tables = []
    opts.passthrough_tables = False
    opts.glyph_names = True
    opts.legacy_kern = True
    opts.hinting = False
    opts.desubroutinize = True
    opts.prune_unicode_ranges = False
    sub = subset.Subsetter(options=opts)
    sub.populate(unicodes=sorted(cps))
    sub.subset(font)
    return font

def main():
    ensure_dirs()
    t0 = time.time()
    sf_path = find_sf_pro()
    if not sf_path:
        sys.exit("[sf] variable SF Pro not found under " + SRC_SF + " - run 01_fetch_sources.py")

    # ---- SF Pro: instance + rescale + subset ---------------------------------
    sf_vf = TTFont(sf_path)
    sf_cmap = sf_vf.getBestCmap()
    sf_cps = sorted(cp for cp in sf_cmap if cp_in_sf(cp))
    log(f"[sf] {len(sf_cps)} codepoints taken from SF Pro (of {len(sf_cmap)} in family)")

    for w in SYNTH_WEIGHTS:
        out = os.path.join(WORK, "sf", f"sf-{w}.ttf")
        f = instancer.instantiateVariableFont(
            sf_vf, {"wght": w, "opsz": 17}, inplace=False, optimize=True)
        scale_upem(f, 1000)
        subset_to_codepoints(f, sf_cps)
        # drop tables that are meaningless after instancing / rescaling
        for t in ("MERG", "trak", "bsln", "meta", "STAT", "DSIG", "HVAR", "MVAR",
                  "avar", "fvar", "gvar", "GDEF"):
            if t in f and t not in ("GDEF",):
                del f[t]
        f.save(out)
        log(f"[sf] wght {w}: {len(f.getBestCmap())} cps, {f['maxp'].numGlyphs} glyphs, "
            f"{os.path.getsize(out)//1024} KiB")

    # ---- PingFang SC: identical subset for every master ----------------------
    pf_fonts = {}
    for name, w in PF_WEIGHTS:
        pf_fonts[name] = TTFont(os.path.join(SRC_PF, f"PingFangSC-{name}.ttf"))
    base_cmap = pf_fonts["Regular"].getBestCmap()
    common_cps = set(base_cmap)
    for name, _ in PF_WEIGHTS:
        common_cps &= set(pf_fonts[name].getBestCmap())
    pf_cps = sorted(cp for cp in common_cps if not cp_in_sf(cp))
    json.dump(sorted(sf_cps), open(os.path.join(WORK, "sf_cps.json"), "w"))
    json.dump(pf_cps, open(os.path.join(WORK, "pf_cps.json"), "w"))
    log(f"[pf] common cps {len(common_cps)}, kept from PingFang {len(pf_cps)}")

    for name, w in PF_WEIGHTS:
        f = pf_fonts[name]
        subset_to_codepoints(f, pf_cps)
        for t in ("VORG", "vhea", "vmtx", "BASE", "meta", "DSIG"):
            if t in f:
                del f[t]
        out = os.path.join(WORK, "pf", f"pf-{w}.ttf")
        f.save(out)
        log(f"[pf] {name} ({w}): {f['maxp'].numGlyphs} glyphs, {os.path.getsize(out)//1024} KiB")
    log(f"done in {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()

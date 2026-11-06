# -*- coding: utf-8 -*-
"""Stage 5: merge CJK + Latin masters, build the variable font, post-process."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables as ot
from fontTools import merge
from fontTools.designspaceLib import (DesignSpaceDocument, AxisDescriptor,
                                      SourceDescriptor, InstanceDescriptor)
from fontTools.varLib import build as varlib_build

STYLE_NAMES = {100: "Ultralight", 200: "Thin", 300: "Light", 400: "Regular",
               500: "Medium", 600: "Semibold", 700: "Bold"}


def style_name(w):
    if w in STYLE_NAMES:
        return STYLE_NAMES[w]
    return f"Weight {w}"


def merge_weight(w):
    out = os.path.join(WORK, "masters", f"master-{w}.ttf")
    if os.path.exists(out):
        return out
    m = merge.Merger()
    font = m.merge([os.path.join(WORK, "masters", f"cjk-{w}.ttf"),
                    os.path.join(WORK, "sf", f"sf-{w}.ttf")])
    font.save(out)
    return out


def check_orders(paths):
    orders = [TTFont(p, lazy=True).getGlyphOrder() for p in paths]
    ref = orders[0]
    for p, o in zip(paths, orders):
        if o != ref:
            raise SystemExit(f"glyph order mismatch in {p}")
    log(f"[merge] {len(paths)} masters share one glyph order of {len(ref)} glyphs")


def src_location(w):
    """Majors outside the exposed axis range are pinned to the lightest stop."""
    return float(max(w, AXIS_MIN))


def make_designspace(paths):
    ds = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.tag, axis.name = "wght", "Weight"
    axis.minimum, axis.default, axis.maximum = AXIS_MIN, AXIS_DEFAULT, AXIS_MAX
    ds.addAxis(axis)
    for (w, path) in paths:
        s = SourceDescriptor()
        s.path = path
        s.name = f"wght{w}"
        s.familyName = FAMILY
        s.styleName = style_name(w)
        s.location = {"Weight": src_location(w)}
        ds.addSource(s)
    for w in INSTANCE_WEIGHTS:
        i = InstanceDescriptor()
        i.familyName = FAMILY
        i.styleName = style_name(w)
        i.postScriptFontName = f"PingFangSFPro-{style_name(w).replace(' ', '')}"
        i.location = {"Weight": float(w)}
        ds.addInstance(i)
    path = os.path.join(WORK, "build", "designspace.designspace")
    ds.write(path)
    return path


def set_name(font, nid, value):
    for rec in list(font["name"].names):
        if rec.nameID == nid:
            font["name"].removeNames(nid)
            break
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        font["name"].setName(value, nid, pid, eid, lid)


def postprocess(font):
    name = font["name"]
    # base names
    set_name(font, 1, FAMILY)
    set_name(font, 2, "Regular")
    set_name(font, 3, f"{VERSION};{AUTHOR};{PS_NAME}")
    set_name(font, 4, FAMILY)
    set_name(font, 5, f"Version {VERSION}")
    set_name(font, 6, PS_NAME)
    set_name(font, 16, FAMILY)
    set_name(font, 17, "Regular")
    set_name(font, 21, FAMILY)
    set_name(font, 22, "Regular")
    set_name(font, 25, FAMILY)
    # CJK-friendly localised family names
    for lid, fam in ((0x804, "苹方 SF Pro"), (0x404, "蘋方 SF Pro")):
        font["name"].setName(fam, 16, 3, 1, lid)
        font["name"].setName(fam, 1, 3, 1, lid)

    os2 = font["OS/2"]
    os2.usWeightClass = 400
    os2.usWidthClass = 5
    os2.fsSelection = (os2.fsSelection & ~0b1100001) | (1 << 6) | (1 << 7)
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = 880, -220, 0
    os2.usWinAscent, os2.usWinDescent = 1060, 340
    os2.achVendID = "KOUF"
    head = font["head"]
    head.unitsPerEm, head.macStyle = 1000, 0
    head.fontRevision = float(VERSION)
    hhea = font["hhea"]
    hhea.ascent, hhea.descent, hhea.lineGap = 1060, -340, 0
    post = font["post"]
    post.formatType = 3.0
    post.isFixedPitch = 0
    font["head"].flags = head.flags

    # minimal GDEF so layout engines classify marks correctly
    gdef = newTable("GDEF")
    gdef.table = ot.GDEF()
    gdef.table.Version = 0x00010000
    gdef.table.GlyphClassDef = ot.GlyphClassDef()
    gdef.table.GlyphClassDef.Format = 2
    classes = {}
    combining = set()
    if "GDEF" in font:  # merged font should not have one, but be safe
        pass
    cmap = font.getBestCmap()
    from fontTools.unicodedata import script, category
    for cp, gname in cmap.items():
        if category(chr(cp)).startswith("M"):
            combining.add(gname)
    for gname in font.getGlyphOrder():
        classes[gname] = 3 if gname in combining else 1
    gdef.table.GlyphClassDef.classDefs = classes
    gdef.table.AttachList = None
    gdef.table.LigCaretList = None
    gdef.table.MarkAttachClassDef = None
    font["GDEF"] = gdef

    # STAT
    try:
        from fontTools.otlLib.builder import buildStatTable
        axes = [{"tag": "wght", "name": "Weight", "ordering": 0,
                 "values": [{"value": w, "name": style_name(w), "flags": 0x2 if w == AXIS_DEFAULT else 0}
                            for w in INSTANCE_WEIGHTS]}]
        buildStatTable(font, axes, elidedFallbackName=2)
        log("[stat] built")
    except Exception as e:  # pragma: no cover
        log(f"[stat] skipped: {e}")

    for tag in ("DSIG", "LTSH", "VDMX", "hdmx"):
        if tag in font:
            del font[tag]
    return font


def main():
    ensure_dirs()
    t0 = time.time()
    paths = []
    for w in SYNTH_WEIGHTS:
        t1 = time.time()
        p = merge_weight(w)
        paths.append((w, p))
        log(f"[merge] wght {w}: {os.path.getsize(p)//1024} KiB ({time.time()-t1:.1f}s)")
    check_orders([p for _, p in paths])
    dspath = make_designspace(paths)
    t1 = time.time()
    vf, model, _ = varlib_build(dspath, optimize=True)
    log(f"[varlib] built in {time.time()-t1:.1f}s")
    postprocess(vf)
    out = os.path.join(DIST, "fonts", "Roboto-Regular.ttf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    vf.save(out)
    log(f"[save] {out} {os.path.getsize(out)/1048576:.1f} MiB")
    log(f"[axes] " + str([(a.axisTag, a.minValue, a.defaultValue, a.maxValue)
                          for a in vf["fvar"].axes]))
    log(f"[instances] " + str([(round(i.coordinates['wght']), style_name(round(i.coordinates['wght'])))
                               for i in vf["fvar"].instances]))
    log(f"total {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

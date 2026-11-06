# -*- coding: utf-8 -*-
"""Validate the synthetic weight model against the real PingFang masters."""
import os, sys, statistics, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from lib.synth import WeightSynthesizer, measure
from lib.raster import polygons, raster, raster_box, iou
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph

SAMPLE = "的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转更单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严龙飞"
SAMPLE = "".join(dict.fromkeys(SAMPLE))[:300]

def main():
    ensure_dirs()
    fonts = {}
    for name, w in PF_WEIGHTS:
        fonts[w] = TTFont(os.path.join(WORK, "pf", f"pf-{w}.ttf"))
    base = TTFont(os.path.join(WORK, "pf", "pf-400.ttf"))
    base_measure = measure(base)
    syn = WeightSynthesizer(base, base_measure)
    cmap = base.getBestCmap()
    names = [cmap[ord(c)] for c in SAMPLE if ord(c) in cmap]
    log(f"sample glyphs: {len(names)}")

    real_measure = {}
    for w in [100, 200, 300, 500, 600]:
        real_measure[w] = measure(fonts[w])

    for w in [100, 200, 300, 500, 600]:
        t0 = time.time()
        test = TTFont(os.path.join(WORK, "pf", "pf-400.ttf"))
        targets = {n: real_measure[w].get(n, (0, 0))[0] for n in test.getGlyphOrder()}
        syn.build(targets, test)
        gs_syn = test.getGlyphSet()
        gs_real = fonts[w].getGlyphSet()
        gs_base = base.getGlyphSet()
        scores, ds = [], []
        for n in names:
            poly_s = polygons(gs_syn, n)
            poly_r = polygons(gs_real, n)
            if not poly_s or not poly_r:
                continue
            import numpy as np
            allp = np.vstack(poly_s + poly_r)
            box = (allp[:, 0].min(), allp[:, 1].min(), allp[:, 0].max(), allp[:, 1].max())
            m1 = raster_box(poly_s, box, 120)
            m2 = raster_box(poly_r, box, 120)
            scores.append(iou(m1, m2))
            a0, p0 = base_measure.get(n, (0, 0))
            ds.append(syn.distance(n, targets.get(n, 0)))
        log(f"wght {w}: IoU mean {statistics.mean(scores):.3f} "
            f"p10 {sorted(scores)[len(scores)//10]:.3f} min {min(scores):.3f} "
            f"| dist mean {statistics.mean(ds):+.1f} units | {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()

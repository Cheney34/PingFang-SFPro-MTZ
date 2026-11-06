# -*- coding: utf-8 -*-
"""Package the built font and previews into a MIUI / HyperOS theme (.mtz)."""
import os, sys, hashlib, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

FONT = os.path.join(DIST, "fonts", "Roboto-Regular.ttf")
PREVIEW = os.path.join(DIST, "preview")
MTZ = os.path.join(DIST, "PingFang-SFPro_v1.0.mtz")

WEIGHTS = "150,200,250,300,350,400,450,500,550,600,650,700"
DESC = ("中文字形取自苹方（PingFang SC），西文、数字与半角标点取自 SF Pro，"
        "单文件变量字体，150–700 连续字重，覆盖系统全部字重档位。"
        "字重说明：400 为苹果苹方 Regular 原版轮廓，其余字重由该轮廓按苹方各字重的真实墨量比例合成，"
        "字形骨架与间距始终保持一致。")
DESC_EN = ("CJK glyphs from PingFang SC, Latin/digits/punctuation from SF Pro. "
           "One variable font file, continuous weight axis 150-700. "
           "Only wght 400 uses the genuine PingFang Regular outlines; the other stops are "
           "synthesised from them by outline offsetting.")

DESCRIPTION_XML = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<theme>
<version><![CDATA[5.6]]></version>
<uiVersion>10</uiVersion>
<author><![CDATA[{AUTHOR}]]></author>
<designer><![CDATA[{AUTHOR}]]></designer>
<title><![CDATA[{THEME_TITLE}]]></title>
<description><![CDATA[{DESC}]]></description>
<fontWeight>{WEIGHTS}</fontWeight>
<authors>
<author locale="zh_CN"><![CDATA[{AUTHOR}]]></author>
<author locale="en_US"><![CDATA[{AUTHOR}]]></author>
</authors>
<designers>
<designer locale="zh_CN"><![CDATA[{AUTHOR}]]></designer>
<designer locale="en_US"><![CDATA[{AUTHOR}]]></designer>
</designers>
<titles>
<title locale="zh_CN"><![CDATA[苹方 SF Pro]]></title>
<title locale="en_US"><![CDATA[{THEME_TITLE}]]></title>
</titles>
<descriptions>
<description locale="zh_CN"><![CDATA[{DESC}]]></description>
<description locale="en_US"><![CDATA[{DESC_EN}]]></description>
</descriptions>
</theme>
'''


def main():
    if not os.path.exists(FONT):
        sys.exit("missing " + FONT + " - run 05_build_vf.py first")
    entries = [("description.xml", os.path.join(WORK, "description.xml"))]
    os.makedirs(WORK, exist_ok=True)
    with open(os.path.join(WORK, "description.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(DESCRIPTION_XML)
    entries.append(("fonts/Roboto-Regular.ttf", FONT))
    for name in sorted(os.listdir(PREVIEW)):
        if name.startswith("preview_fonts"):
            entries.append(("preview/" + name, os.path.join(PREVIEW, name)))
    with zipfile.ZipFile(MTZ, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for arc, path in entries:
            z.write(path, arc)
            print(f"  + {arc:38s} {os.path.getsize(path):>10,}")
    size = os.path.getsize(MTZ)
    print(f"[mtz] {MTZ}  {size/1048576:.1f} MiB")
    h = hashlib.sha256(open(MTZ, "rb").read()).hexdigest()
    print("[sha256]", h)
    with open(os.path.join(DIST, "PingFang-SFPro_v1.0.mtz.sha256"), "w", encoding="utf-8") as f:
        f.write(h + "  PingFang-SFPro_v1.0.mtz\n")
    with zipfile.ZipFile(MTZ) as z:
        bad = z.testzip()
        print("[verify] entries:", len(z.namelist()), "corrupt:", bad)


if __name__ == "__main__":
    main()

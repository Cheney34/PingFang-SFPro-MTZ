# -*- coding: utf-8 -*-
"""Render MIUI theme store previews from the built variable font.

Produces preview/preview_fonts_0..3.jpg (1080x1920) and
preview/preview_fonts_small_0.png (285x74) inside dist/.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from PIL import Image, ImageDraw, ImageFont

VF = os.path.join(DIST, "fonts", "Roboto-Regular.ttf")
OUT = os.path.join(DIST, "preview")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920
BG_TOP = (11, 15, 20)
BG_BOT = (19, 26, 36)
INK = (232, 240, 248)
INK_DIM = (127, 166, 204)
INK_MUTE = (94, 113, 134)
ACCENT = (90, 176, 255)
FAINT = (34, 48, 63)

_cache = {}


def font(size, wght=400):
    key = (size, wght)
    if key not in _cache:
        f = ImageFont.truetype(VF, size)
        f.set_variation_by_axes([wght])
        _cache[key] = f
    return _cache[key]


def background():
    img = Image.new("RGB", (W, H), BG_TOP)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(a + (b - a) * t ** 0.85) for a, b in zip(BG_TOP, BG_BOT))
        d.line([(0, y), (W, y)], fill=c)
    # soft accent glow in the top-right corner
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(90):
        r = 620 - i * 6
        a = int(26 * (1 - i / 90) ** 2)
        gd.ellipse([W - 260 - r, -220 - r, W - 260 + r, -220 + r], fill=(a, a * 2, a * 3))
    return Image.blend(img, Image.blend(img, glow, 0.5), 0.35) if False else Image.fromarray(
        __import__("numpy").clip(
            __import__("numpy").asarray(img, dtype="int16") + __import__("numpy").asarray(glow, dtype="int16") // 3,
            0, 255).astype("uint8"))


def text(d, xy, s, size, wght=400, fill=INK, anchor="la", max_w=None, min_size=14):
    """Draw text, shrinking the size until it fits inside max_w."""
    f = font(size, wght)
    if max_w:
        while size > min_size and d.textlength(s, font=f) > max_w:
            size -= 2
            f = font(size, wght)
    d.text(xy, s, font=f, fill=fill, anchor=anchor)
    return f


def rule(d, y, x0=80, x1=W - 80, fill=(30, 42, 56), width=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def header(img, kicker, title, sub):
    d = ImageDraw.Draw(img)
    text(d, (80, 132), kicker, 30, 500, ACCENT)
    text(d, (80, 190), title, 92, 600, INK, max_w=W - 160)
    text(d, (80, 320), sub, 34, 400, INK_DIM, max_w=W - 160)
    rule(d, 400)
    return d


def card_weights():
    img = background()
    d = header(img, "PINGFANG SF PRO", "字重阶梯", "可变字重 150 · 200 · 300 · 400 · 500 · 600 · 700")
    weights = [150, 200, 300, 400, 500, 600, 700]
    labels = {150: "极细", 200: "纤细", 300: "细体", 400: "常规", 500: "中等", 600: "中粗", 700: "粗体"}
    y = 470
    for w in weights:
        text(d, (80, y + 18), str(w), 40, 500, INK_MUTE)
        text(d, (80, y + 62), labels[w], 24, 400, (70, 88, 106))
        text(d, (250, y), "永字八法 Aa 壹貳", 84, w, INK, max_w=W - 330)
        y += 168
    rule(d, y + 10, fill=(26, 36, 48))
    text(d, (80, y + 44), "中文轮廓源自苹方（PingFang SC）Regular，西文与数字源自 SF Pro", 26, 400, (74, 92, 112), max_w=W - 160)
    return img


def card_cjk():
    img = background()
    d = header(img, "中文 · PINGFANG", "苹方骨架", "30,000+ 中日韩字符 · 单文件变量字体")
    cells = [(80, 460, "永", 150), (580, 460, "字", 300), (80, 900, "八", 500), (580, 900, "法", 700)]
    for x, y, ch, w in cells:
        d.rounded_rectangle([x, y, x + 420, y + 380], radius=28, fill=(20, 28, 38), outline=(32, 44, 58), width=2)
        text(d, (x + 210, y + 150), ch, 240, w, INK, anchor="mm")
        text(d, (x + 34, y + 326), f"wght {w}", 26, 400, INK_MUTE)
    y = 1340
    lines = ["中文字形取自苹果苹方，笔画收尾利落、字面方正；",
             "西文、数字与半角标点取自 SF Pro，两者度量统一。",
             "150–700 连续字重，覆盖系统全部字重档位。"]
    for ln in lines:
        text(d, (80, y), ln, 36, 400, (196, 210, 224), max_w=W - 160)
        y += 58
    return img


def card_latin():
    img = background()
    d = header(img, "西文 · SF PRO", "西文与数字", "SF Pro Display / Text · 光学尺寸已固定")
    text(d, (80, 470), "Aa Bb Cc", 150, 700, INK, max_w=W - 160)
    text(d, (80, 660), "0123456789", 118, 300, INK_DIM, max_w=W - 160)
    y = 830
    for w, s in [(200, "ABCDEFGHIJKLMNOPQRSTUVWXYZ"), (400, "abcdefghijklmnopqrstuvwxyz"), (600, "AaBbCcDdEeFfGg 0123456789")]:
        text(d, (80, y), f"{w}", 26, 400, INK_MUTE)
        text(d, (140, y - 18), s, 54, w, (214, 226, 238), max_w=W - 240)
        y += 120
    rule(d, y + 20, fill=(26, 36, 48))
    text(d, (80, y + 56), "「永字八法」永字八法 · SF Pro · 0123", 44, 400, (170, 190, 210), max_w=W - 160)
    return img


def card_sample():
    img = background()
    d = header(img, "排版样张 · SAMPLE", "苹方 SF Pro", "一个文件，覆盖全系统字重")
    text(d, (80, 470), "永字八法，笔墨相生。", 76, 600, INK, max_w=W - 160)
    body = ["横竖撇捺之间，字形比例与原版苹方保持一致；",
            "西文以 SF Pro 呈现，行距与字面高度整体统一。",
            "The quick brown fox jumps over the lazy dog.",
            "数字 0123456789 · 标点 ，。、；：「」（）"]
    y = 610
    for ln in body:
        text(d, (80, y), ln, 40, 400, (186, 202, 218), max_w=W - 160)
        y += 74
    y += 30
    rule(d, y, fill=(26, 36, 48))
    y += 50
    for w in (300, 500, 700):
        text(d, (80, y), f"wght {w}", 26, 400, INK_MUTE)
        text(d, (80, y + 34), "永字八法 PingFang SF Pro 0123", 62, w, INK, max_w=W - 160)
        y += 150
    return img


def small():
    w, h = 285, 74
    img = Image.new("RGB", (w, h), BG_TOP)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(BG_TOP, (26, 36, 48))))
    d.rectangle([0, 0, 512, h], fill=None)
    d.rectangle([0, 0, 6, h], fill=ACCENT)
    text(d, (22, 30), "苹方 SF Pro", 34, 500, INK, anchor="lm", max_w=w - 40)
    return img


def main():
    jobs = [("preview_fonts_0.jpg", card_weights), ("preview_fonts_1.jpg", card_cjk),
            ("preview_fonts_2.jpg", card_latin), ("preview_fonts_3.jpg", card_sample)]
    for name, fn in jobs:
        img = fn()
        p = os.path.join(OUT, name)
        img.save(p, "JPEG", quality=92, optimize=True, progressive=True)
        print(name, img.size, f"{os.path.getsize(p)/1024:.0f} KiB")
    img = small()
    p = os.path.join(OUT, "preview_fonts_small_0.png")
    img.save(p, "PNG", optimize=True)
    print("preview_fonts_small_0.png", img.size, f"{os.path.getsize(p)/1024:.0f} KiB")


if __name__ == "__main__":
    main()

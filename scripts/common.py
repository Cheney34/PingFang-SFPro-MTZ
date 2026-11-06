# -*- coding: utf-8 -*-
"""Shared helpers for the PingFang x SF Pro MIUI/HyperOS font build."""
import os, sys, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(REPO, "work")
DIST = os.path.join(REPO, "dist")
PF_ROOT = os.path.join(REPO, "src-pingfang")     # git clone target
SRC_PF = os.path.join(PF_ROOT, "ttf")            # .../PingFangSC-*.ttf live here
SRC_SF = os.path.join(REPO, "src-sfpro")

# PingFang SC static weights shipped by refinec/PingFangSC (upem 1000, glyf).
PF_WEIGHTS = [
    ("Ultralight", 100),   # Apple's Ultralight is the lightest face
    ("Thin", 200),
    ("Light", 300),
    ("Regular", 400),
    ("Medium", 500),
    ("Semibold", 600),
]
# The theme exposes an extrapolated 700 master so that the wght axis ends on a
# real outline instead of relying on varLib extrapolation.
SYNTH_WEIGHTS = [w for _, w in PF_WEIGHTS] + [700]

AXIS_MIN, AXIS_DEFAULT, AXIS_MAX = 150, 400, 700
INSTANCE_WEIGHTS = [150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700]

# Codepoint ranges taken from SF Pro. Everything else comes from PingFang SC.
SF_RANGES = [
    (0x0020, 0x007E),  # Basic Latin
    (0x00A0, 0x024F),  # Latin-1 Supplement, Latin Extended-A/B
    (0x0250, 0x02AF),  # IPA Extensions
    (0x02B0, 0x02FF),  # Spacing Modifier Letters
    (0x0300, 0x036F),  # Combining Diacritics
    (0x0370, 0x03FF),  # Greek
    (0x0400, 0x04FF),  # Cyrillic
    (0x1E00, 0x1EFF),  # Latin Extended Additional
    (0x2000, 0x206F),  # General Punctuation
    (0x2070, 0x209F),  # Super/Subscripts
    (0x20A0, 0x20BF),  # Currency Symbols
    (0x2100, 0x214F),  # Letterlike Symbols
    (0x2150, 0x218F),  # Number Forms
    (0x2190, 0x21FF),  # Arrows
    (0x2200, 0x22FF),  # Mathematical Operators
    (0x2300, 0x23FF),  # Misc Technical
    (0x2500, 0x257F),  # Box Drawing
    (0x25A0, 0x25FF),  # Geometric Shapes
    (0x2600, 0x26FF),  # Misc Symbols
    (0x2700, 0x27BF),  # Dingbats
]

FAMILY = "PingFang SF Pro"
PS_NAME = "PingFangSFPro-Regular"
THEME_TITLE = "PingFang SF Pro"
AUTHOR = "KOUFIK"
VERSION = "1.000"


def find_sf_pro(root=None):
    """Locate the variable SF Pro file anywhere under src-sfpro/."""
    root = root or SRC_SF
    for dirpath, _, filenames in os.walk(root):
        for name in sorted(filenames):
            if name.lower().startswith("sf-pro") and name.lower().endswith((".ttf", ".otf")):
                return os.path.join(dirpath, name)
    return None


def cp_in_sf(cp):
    return any(a <= cp <= b for a, b in SF_RANGES)


def log(*a):
    print(*a, flush=True)


def ensure_dirs():
    for d in (WORK, DIST, os.path.join(WORK, "pf"), os.path.join(WORK, "sf"),
              os.path.join(WORK, "masters"), os.path.join(WORK, "build")):
        os.makedirs(d, exist_ok=True)

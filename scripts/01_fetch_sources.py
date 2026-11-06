# -*- coding: utf-8 -*-
"""Stage 1: fetch the two source font families.

    python scripts/01_fetch_sources.py

PingFang SC  -> https://github.com/refinec/PingFangSC  (open mirror of Apple's ttf faces)
SF Pro       -> https://hk.maisfontes.com/sf-pro.font  (variable font, opsz + wght axes)

Both families are Apple proprietary.  This script only downloads them into
src-pingfang/ and src-sfpro/, which are git-ignored: the repository itself
never redistributes the binaries.
"""
import os, sys, json, zipfile, shutil, subprocess, urllib.request, urllib.parse, http.cookiejar

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PF_ROOT, SRC_PF, SRC_SF, find_sf_pro

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
PF_REPO = "https://github.com/refinec/PingFangSC"
SF_PAGE = "https://hk.maisfontes.com/sf-pro.font"
SF_API = "https://hk.maisfontes.com/main/downloadFont"


def log(*a):
    print(*a, flush=True)


# --------------------------------------------------------------------------- pingfang
def have_pingfang():
    return os.path.exists(os.path.join(SRC_PF, "PingFangSC-Regular.ttf"))


def fetch_pingfang():
    if have_pingfang():
        log("[pingfang] already present")
        return
    os.makedirs(PF_ROOT, exist_ok=True)
    git = shutil.which("git") or r"D:\Program Files\Git\cmd\git.exe"
    if os.path.exists(git):
        log("[pingfang] git clone --depth 1", PF_REPO)
        r = subprocess.run([git, "clone", "--depth", "1", PF_REPO + ".git", PF_ROOT],
                           capture_output=True, text=True)
        if r.returncode == 0 and have_pingfang():
            log("[pingfang] ok")
            return
        log("[pingfang] clone failed, falling back to zip:", (r.stderr or "").strip()[:200])
    # zip fallback
    for branch in ("main", "master"):
        url = f"https://codeload.github.com/refinec/PingFangSC/zip/refs/heads/{branch}"
        try:
            tmp = os.path.join(PF_ROOT, "_pf.zip")
            log("[pingfang] downloading", url)
            urllib.request.urlretrieve(url, tmp)
            with zipfile.ZipFile(tmp) as z:
                top = os.path.commonprefix(z.namelist()).split("/")[0]
                z.extractall(PF_ROOT)
            inner = os.path.join(PF_ROOT, top)
            for name in os.listdir(inner):
                shutil.move(os.path.join(inner, name), os.path.join(PF_ROOT, name))
            os.rmdir(inner)
            os.remove(tmp)
            if have_pingfang():
                log("[pingfang] ok")
                return
        except Exception as e:
            log("[pingfang] zip failed:", e)
    sys.exit("[pingfang] could not obtain PingFangSC-Regular.ttf - download the repo "
             "manually, then move its ttf/ folder to " + SRC_PF)


# ------------------------------------------------------------------------------- sf pro
def have_sfpro():
    return find_sf_pro() is not None


def fetch_sfpro():
    if have_sfpro():
        log("[sfpro] already present:", find_sf_pro())
        return
    os.makedirs(SRC_SF, exist_ok=True)
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [("User-Agent", UA), ("Accept-Language", "zh-HK,zh;q=0.9,en;q=0.8")]

    log("[sfpro] GET", SF_PAGE)
    html = opener.open(SF_PAGE, timeout=60).read().decode("utf-8", "replace")
    import re
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    csrf = m.group(1) if m else ""
    m = re.search(r'data-font-token="([^"]+)"', html)
    if not m:
        sys.exit("[sfpro] could not find the download token on the page - "
                 "download SF Pro manually into " + SRC_SF)
    token = m.group(1)
    payload = json.dumps({"token": token, "src": "modal"}).encode()
    req = urllib.request.Request(SF_API, data=payload, method="POST", headers={
        "Content-Type": "application/json;charset=UTF-8",
        "X-CSRF-TOKEN": csrf,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": SF_PAGE,
        "Origin": "https://hk.maisfontes.com",
        "User-Agent": UA,
    })
    try:
        data = json.loads(opener.open(req, timeout=60).read().decode("utf-8", "replace"))
    except Exception as e:
        sys.exit(f"[sfpro] download request failed ({e}) - download SF Pro manually into " + SRC_SF)
    url = data.get("url") or (data.get("data") or {}).get("url")
    if not url:
        sys.exit("[sfpro] unexpected response: " + str(data)[:200])
    log("[sfpro] downloading", url)
    tmp = os.path.join(SRC_SF, "sfpro.zip")
    with opener.open(url, timeout=180) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f)
    with zipfile.ZipFile(tmp) as z:
        z.extractall(SRC_SF)
    os.remove(tmp)
    p = find_sf_pro()
    if not p:
        sys.exit("[sfpro] archive did not contain a variable sf-pro font")
    log("[sfpro] ok:", p)


def main():
    fetch_pingfang()
    fetch_sfpro()
    log("\nnext:  python scripts/02_prepare_sources.py")


if __name__ == "__main__":
    main()

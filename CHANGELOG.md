# 变更记录

版本号规则：项目、MTZ、包内字体共用 `1.0-demo` / `v1.0.0-demo`；
`description.xml` 的 `<version>` 仍写主题规范的 5.6（那是主题引擎的协议版本，不是本项目版本）。

---

## 1.0-demo — 2026-11-06 — 首个 Demo

苹方 × SF Pro 的第一版：把「中西文各取所长 + 单文件变量字体」这条链路跑通，
出一份能装进手机的 MTZ，并把这套做法固化成 7 个可复现的脚本。

### 新增

- **`scripts/01_fetch_sources.py`**：一次拿全两套源字体。苹方走
  [refinec/PingFangSC](https://github.com/refinec/PingFangSC)（`git clone --depth 1`，
  失败自动回落 codeload zip）；SF Pro 走 maisfontes 的 token 流程
  （`GET` 页面取 `data-font-token` → `POST /main/downloadFont` → 下载 zip）。
  两条路径都实测从零跑通。
- **`scripts/02_prepare_sources.py`**：SF Pro 按字重实例化、opsz 固定 17、upem 2048→1000，
  再裁剪到 1,485 个拉丁 / 希腊 / 西里尔 / 数字 / 半角标点码位；苹方取这些码位的**补集**，
  保证 7 个母版字形集合完全一致（31,754 glyph 同一 glyph order）。
- **`scripts/lib/synth.py`**：轮廓外扩 / 内缩求解。miter 法线 + 每点碰撞钳制
  （最近异轮廓点距离 × 0.45），面积-距离关系给初值，Newton 迭代不超过 5 轮。
- **`scripts/04_build_masters.py`**：由苹方 Regular 合成 100–700 共 7 个母版
  （400 直接复用原版；700 由 500 / 600 线性外推 ×0.9）。
  收敛后残余面积误差：200 档 1.3%、300 档 1.2%、500 档 0.9%、600 档 1.1%、700 档 1.3%、100 档 8.1%。
- **`scripts/05_build_vf.py`**：`merge` 中西文母版 → `varLib.build(optimize=True)` →
  后处理（name 表全语言名称、OS/2 `usWeightClass=400` / typo 880 -220 / win 1060 340、
  hhea 1060 -340 0、`post` 3.0、最小 GDEF、`STAT` 12 个实例、删掉 DSIG/LTSH/VDMX/hdmx）。
- **`scripts/06_previews.py` / `07_package_mtz.py`**：Pillow 渲染 1080×1920 预览图与
  285×74 小图；生成 `description.xml` 并打成 MTZ，结构对齐 *Chiron-Merriweather v6.3*。

### 修正过的坑（都写进注释了，别重复踩）

- **varLib 轴越界**：母版位置 100 落在 `wght` 轴 150–700 之外会直接报
  `VarLibValidationError`。做法是把 100 母版**钉到轴端点 150** 再构建，轴外由系统夹取。
- **轮廓绕向**：苹方有部分字（「四」`uni56DB` 等）轮廓绕向与常规相反，法线朝内会让
  「外扩反而变细」，Newton 迭代直接发散（面积误差 254% → 295%）。现在用
  「沿法线跳 3 个单位后是否落在墨内」做经验探测，翻转整条轮廓的法线方向。
- **字重映射**：Apple 的 `Ultralight` 比 `Thin` **更细**（墨量比 0.345 vs 0.514），
  这两个名字直觉上容易反向映射，本项目按墨量实测结果定为 Ultralight=100、Thin=200。
- **`GlyphCoordinates`**：fontTools 的 `glyf.recalcBounds` 要求 `coordinates` 是
  `GlyphCoordinates` 而不是 list，否则抛 `calcIntBounds` 的 AttributeError。

### 已知未做

| 项 | 原因 |
|---|---|
| 真机长测 | 校验只在 fontTools / FreeType 层完成：表格、实例化面积比（150→0.309、400→1.000、700→1.533）、渲染墨量单调性、192,994 条轮廓的完整性 |
| Root 模块 | 本 Demo 只出 MTZ |
| Apple emoji | 不在本包范围 |
| 100 档精度 | 极细笔画受碰撞钳制，面积误差 8.1% 收敛不下去 |
| 中文真实字重 | 苹方 6 个字重轮廓互不兼容，除非重建拓扑，否则只能合成 |

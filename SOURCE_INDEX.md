# 源码索引（2026-11-06）

对应出货版本 **v1.0.0-demo**。

| 源码 | 对应产物 | 说明 |
|---|---|---|
| `scripts/01_fetch_sources.py` | `src-pingfang/ttf/PingFangSC-*.ttf`、`src-sfpro/*/sf-pro.ttf` | 下载源字体 |
| `scripts/02_prepare_sources.py` | `work/sf/sf-{100..700}.ttf`、`work/pf/pf-{100..600}.ttf` | 实例化 + 缩放 + 裁剪 |
| `scripts/03_validate_synth.py` | — | 面积-距离单调性自检 |
| `scripts/04_build_masters.py` | `work/masters/cjk-{100..700}.ttf` | 合成 CJK 母版 |
| `scripts/05_build_vf.py` | `dist/fonts/Roboto-Regular.ttf` | 合并 + varLib + 后处理 |
| `scripts/06_previews.py` | `dist/preview/preview_fonts_0..3.jpg`、`preview_fonts_small_0.png` | 主题商店预览图 |
| `scripts/07_package_mtz.py` | `dist/PingFang-SFPro_v1.0.mtz` | 打包 MTZ |
| `scripts/common.py` | — | 字重表、码位范围、命名、路径 |
| `scripts/lib/synth.py` | — | 轮廓外扩 / 内缩求解（numpy） |
| `scripts/lib/raster.py` | — | 轮廓光栅化（面积 / IoU 测量） |

## 关键常量

```python
PF_WEIGHTS      = UltraLight 100, Thin 200, Light 300, Regular 400, Medium 500, Semibold 600
SYNTH_WEIGHTS   = 上面 6 个 + 700（外推）
AXIS_MIN/DEFAULT/MAX = 150 / 400 / 700
INSTANCE_WEIGHTS     = 150..700 step 50（与 description.xml 的 <fontWeight> 一一对应）
SF_RANGES            = 拉丁 / 希腊 / 西里尔 / 数字 / 半角标点 / 符号箭头 20 段
```

改字重范围、换西文范围、换家族名，都只需要动 `scripts/common.py`。

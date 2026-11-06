# 苹方 × SF Pro 变量字体主题 v1.0.0-demo

> **这是 Demo，不是正式版。** 流水线跑通、产物能装能用，但没有真机长测；
> 中文字重除 Regular(400) 以外全部由 Regular 几何合成。

把 **苹方（PingFang SC）的中文骨架** 和 **SF Pro 的西文 / 数字** 装进一个
**单文件变量字体**，wght 轴 150–700 连续可调，打成 MIUI / HyperOS 主题包。

---

## 附件

| 文件 | 体积 | 说明 |
|---|---|---|
| `PingFang-SFPro_v1.0.mtz` | 21.2 MiB（22,226,186 B） | 主题包本体，免 Root |
| `PingFang-SFPro_v1.0.mtz.sha256` | 91 B | `a3645b4e8f8db45b36d03fede529b333f9cdff8bd55cb308eec0b7559d9d8be0` |

## 装法

1. 下载 `PingFang-SFPro_v1.0.mtz`；
2. 设置 → 主题壁纸（主题商店）→ 我的 → 主题 → 从 SD 卡导入 / 本地导入；
3. 应用「苹方 SF Pro」，重启一次更稳妥；
4. 设置 → 显示 → 字体，能在 150–700 之间拖字重即成功。

> 提示「主题不兼容 / 签名校验失败」时，说明你的机型签名策略不同，需要自己重签再导入。

## 包里是什么

- `description.xml`：version 5.6 / uiVersion 10，`<fontWeight>` 150–700 共 12 档，
  中文 + en_US 本地化块，与字体 `fvar` 实例一一对应；
- `fonts/Roboto-Regular.ttf`：31,754 glyph / 30,666 cmap，`wght` 150–700、默认 400、12 个命名实例；
- `preview/preview_fonts_0..3.jpg`（1080×1920）+ `preview_fonts_small_0.png`（285×74）。

中西文分工：CJK / 假名 / 全角标点 / 注音 约 29,180 码位取苹方；拉丁 / 希腊 / 西里尔 /
数字 / 半角标点 1,485 码位取 SF Pro（opsz 固定 17，upem 2048→1000）。

## 已知限制（先看这一段再决定要不要装）

| 限制 | 说明 |
|---|---|
| 只有 400 是苹果原版轮廓 | 其余 6 档是几何合成，收笔端点与复杂字内部空间跟 Apple 真身有差异 |
| 细字重偏粗 | 碰撞钳制会让极细笔画提前停止收缩，100 档面积误差约 8% |
| 未真机长测 | 校验都在 fontTools / FreeType 层：表格完整性、实例化面积比、渲染墨量单调性、192,994 条轮廓完整性 |
| 无 Root 通道 | 本 Demo 只出 MTZ，没有 Magisk / KernelSU 模块 |
| 不含 emoji | 只换字体；emoji 见作者另一个项目 chiron-apple-emoji |
| 酷安 / 微博不跟随 | 这类 App 自带字体或渲染器，任何系统级替换都无效 |

合成质量对照（25 个随机 CJK 的轮廓 IoU，合成 vs 苹果真身 / 基线 = 直接把 Regular 当该字重）：

| 字重 | 合成 | 基线 |
|---|---|---|
| 200 Thin | 0.534 | 0.514 |
| 300 Light | 0.828 | 0.775 |
| 500 Medium | 0.863 | 0.780 |
| 600 Semibold | 0.825 | 0.717 |

## 授权与分发

苹方（PingFang SC）与 SF Pro 的版权属于 **Apple Inc.**，均为专有字体、无公开再分发授权。
本仓库只分发构建脚本，不分发字体二进制。

本 Release 附件是**作者本机自用的 Demo 构建，仅供个人试用，不得再分发、不得商用**，
附件的存在不构成对上述字体的任何授权。详见 [THIRD-PARTY.md](https://github.com/Cheney34/PingFang-SFPro-MTZ/blob/main/THIRD-PARTY.md)。

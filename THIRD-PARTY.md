# 第三方资源与授权

本仓库**只分发代码**（构建脚本）。字体由使用者在本地从合法来源获取，再用脚本处理。

| 资源 | 权利方 | 授权 | 能否再分发 |
|---|---|---|---|
| PingFang SC（苹方） | Apple Inc. | **专有**，无公开授权 | ❌ 不可 |
| SF Pro | Apple Inc. | **专有**，无公开授权 | ❌ 不可 |
| [refinec/PingFangSC](https://github.com/refinec/PingFangSC) 镜像仓库 | 第三方整理 | 仓库自身声明见其 LICENSE，但**不改变字体本身的 Apple 版权** | ❌ 字体仍不可再分发 |
| [maisfontes](https://hk.maisfontes.com/sf-pro.font) SF Pro 打包 | 第三方整理 | 同上 | ❌ |
| fontTools / numpy / Pillow | 各自社区 | MIT / BSD / HPND | ✅ |

## 关于字体

苹方与 SF Pro 的版权属于 Apple。即便拿到了 ttf，**不因为拿到手就获得再分发权**。

因此本仓库：

- **不提供** `.ttf`、`.mtz` 等含 Apple 字形的产物（`src-*`、`work/`、`dist/` 均 `.gitignore`）；
- 提供 7 个脚本，由使用者用自己的合法来源生成。

## 关于本 Demo 的 Release 附件

`v1.0.0-demo` 的 Release 附件里放了 `PingFang-SFPro_v1.0.mtz`，那是**作者本机自用、供试用验证的 Demo 构建**：

- 仅供个人设备上试用，**不得再分发、不得商用**；
- 附件的存在不构成对苹方 / SF Pro 的任何授权，也不改变上述授权状况；
- 如果你要公开发布自己的成品，请自行评估风险 —— 这不是技术问题，我不能替你下判断。

## 字体元数据

构建脚本会改写 `name` 表（家族名 `PingFang SF Pro`）。改度量、换西文属于**衍生**而非**原创**，
分发产物时请保留原字体的版权字段。

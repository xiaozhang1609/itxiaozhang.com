---
title: Blender老版本
permalink: /blender-old-versions/
date: 2024-01-04 15:42:06
categories: 
  - 技术笔记
tags: 
  - 电脑维修
---

 [GitHub](https://github.com/ "Github")

[nalexandru/BlenderCompat](https://github.com/nalexandru/BlenderCompat)

# BlenderCompat
<!--more-->

## Windows 7 支持 Blender 3.x 及更高版本

### 描述

此仓库包含一个兼容性 DLL，用于在 Windows 7 上运行 Blender 3.x，并包含一个补丁来修改 Blender 源代码以使用它。它通过将 bcompat7 添加到库列表的前面来实现，因此它使用其中的入口点，而不是系统库中的入口点。

### 二进制文件

- **稳定版本**：从与官方发布相同的提交编译而来，在发布页面上可获得。

- **最新构建版本**：由 Loriem 提供的更多最新构建版本，包括预发布版本，可在此处获得：[Loriem's Dropbox](https://www.dropbox.com/sh/eufffe60fvtr9mz/AAA0YtogOoJTKggWtgAXRyXJa?dl=0)

### 与官方发布相比的更改

- 回退了 [T97828](https://developer.blender.org/T97828) 由于 AMD Polaris GPU 上的渲染问题（问题 #18、#19）

## 为 Windows 7 构建 Blender

按照这些指示构建 Blender：[Building Blender for Windows](https://wiki.blender.org/wiki/Building_Blender/Windows)，但有一个小改动。在运行 make update 之前，将 bcompat7.patch 复制到 blender 源代码树中，并运行 git apply bcompat7.patch（会有一些关于空白的警告，可以忽略），然后继续按照指南进行。

要使用您自己构建的此兼容性 DLL，请在运行 make update 后覆盖 lib/win64\_vc15/bcompat7 目录中的文件。

### 3.5 及更高版本

从 3.5 版开始，一些静态库被切换为共享，如 Blender 3.5 的库变化所述。

当 OpenEXR 针对 Windows 8 或更高版本构建时，它会使用 CreateFile2 而不是 CreateFile，而 CreateFile2 不在 Windows 7 上。因此，Blender 的库仓库中的 OpenEXR.dll 将无法工作。

为了解决这个问题，在构建 Blender 之前（在 make update 之后），您必须构建 OpenEXR。为此，请克隆 OpenEXR 仓库（为避免问题，请克隆仓库中存在的版本），在 OpenEXR 源代码中应用此仓库中的 openexr\_w7.patch，然后运行 build.cmd 。OpenEXR 文件将被复制到 openexr\\bin 中，覆盖现有文件。

#### api-ms-win-core-path-l1-1-0.dll

除此 DLL 外，运行 Blender 还需要 api-ms-win-core-path-l1-1-0.dll，由于 Python 的原因。此库的 Windows 7 版本可在此处找到：[GitHub - api-ms-win-core-path-HACK](https://github.com/nalexandru/api-ms-win-core-path-HACK)

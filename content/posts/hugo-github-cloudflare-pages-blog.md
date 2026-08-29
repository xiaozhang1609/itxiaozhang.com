---
title: 'Windows 11 从零搭建个人博客：Hugo + GitHub + Cloudflare Pages'
url: posts/hugo-github-cloudflare-pages-blog
date: 2026-08-29T18:21:37+08:00
description: 面向零基础读者，使用 Windows 11、Hugo、GitHub 与 Cloudflare Pages，从本地写作到自动部署，搭建一个免费、可持续更新的个人博客；文末附 .com 自定义域名绑定教程。
categories:
  - 技术文章
tags:
  - Hugo
author: IT小章
---

> 原文地址：<https://itxiaozhang.com/posts/hugo-github-cloudflare-pages-blog>  

> 本文应**二狗肉包子**的建议撰写。

> 最后核对：2026-08-29。本文按 Windows 11、Hugo 最新稳定版、GitHub 与 Cloudflare 当前网页流程编写。软件版本和按钮名称会变化；遇到差异时，请优先相信终端输出和文末官方文档。

你不需要会编程，也不需要先学完 Git。本教程会带你完成这条完整链路：

```text
在 VS Code 写 Markdown 文章
        ↓
Hugo 生成静态网站
        ↓
Git 推送源码到 GitHub
        ↓
Cloudflare Pages 自动构建并发布
        ↓
得到一个 https://你的项目.pages.dev 博客
        ↓
（可选）购买 .com 并绑定自己的域名
```

最终你会有一个名为“我的个人博客”的简洁文章列表网站，并能在以后用一套固定流程持续发布文章。


## 先看时间、成本和准备清单

不购买域名时，第一次完成大约需要 45～75 分钟；购买和绑定 `.com` 域名通常再需要 15～30 分钟。

| 项目 | 是否收费 | 本文是否必须 |
| --- | --- | --- |
| VS Code、Git、Hugo | 免费 | 必须 |
| GitHub 公开仓库 | 免费 | 必须 |
| Cloudflare Pages | 免费 | 必须 |
| `.com` 域名 | 付费，价格与续费价以购买页为准 | 可选 |

准备好：Windows 11 电脑、可联网的浏览器、一个可收邮件的邮箱，以及域名章节所需的有效付款方式。

> **中国大陆读者提示**：GitHub 和 Cloudflare 均为境外服务，访问体验会受网络环境影响。本文不涵盖 ICP 备案、中国大陆机房托管或境内访问优化。

> **安全提醒**：不要把密码、GitHub Token、Cloudflare API Token、付款资料或私密图片放进公开 GitHub 仓库。截图时也要遮住邮箱、账户资料与付款信息。

---

## 1. 先理解四个工具各做什么

- **Markdown**：一种很轻的写作格式。你写标题、段落和图片地址；它不是网页代码。
- **Hugo**：把 Markdown 文章和主题转换成一套静态网页。
- **Git 与 GitHub**：Git 在本机记录每次改动；GitHub 把这份项目备份在网上。
- **Cloudflare Pages**：发现 GitHub 有新提交后，自动运行 Hugo 并把生成的网站发布到公网。

因此，你日后不需要手动上传网页文件。只要把文章推送到 GitHub，Cloudflare Pages 就会自动更新网站。

---

## 2. 注册 GitHub 与 Cloudflare

### 2.1 注册 GitHub

打开 [GitHub](https://github.com/)，点击 **Sign up（注册）**，按提示用邮箱注册并完成邮箱验证。



记下你的 GitHub 用户名。后面仓库网址会用到它，例如：

```text
https://github.com/你的用户名/my-hugo-blog
```

为了不让提交记录公开你的真实邮箱，注册后可打开 GitHub 的 **Settings → Emails**，勾选 **Keep my email addresses private**，然后复制页面提供的 `noreply` 邮箱地址，稍后填给 Git。

### 2.2 注册 Cloudflare

打开 [Cloudflare](https://dash.cloudflare.com/sign-up)，创建账户并验证邮箱。



本教程不展开账户安全设置；但无论在哪个平台，都不要向任何人发送密码或验证码。

---

## 3. 安装 VS Code、Git 和 Hugo Extended

### 3.1 安装 VS Code 和中文语言包

1. 打开 [VS Code 官网](https://code.visualstudio.com/)，下载 Windows 安装包并安装。
2. 启动 VS Code，点击左侧 **Extensions（扩展）**。
3. 搜索 `Chinese (Simplified) Language Pack for Visual Studio Code`，安装后按提示重启。



之后通过顶部菜单 **终端 → 新建终端** 打开内置终端。终端右上角的配置文件应为 **PowerShell**。



### 3.2 安装 Git

1. 打开 [Git for Windows](https://git-scm.com/download/win) 下载并启动安装程序。
2. 安装过程大部分保持默认；出现下列选项时确认：
   - 默认编辑器选择 **Visual Studio Code**；
   - PATH 选择允许从命令行使用 Git 的选项；
   - 凭据管理器保持 **Git Credential Manager**。
3. 完成安装后，关闭并重新打开 VS Code 的 PowerShell。

运行：

```powershell
git --version
```

看到类似 `git version 2.x.x` 即成功。

如果看不到：先完全关闭并重开 VS Code；仍不行时重启电脑，再确认 Git 是否安装完成。

### 3.3 用 winget 安装 Hugo Extended

在 VS Code 的 PowerShell 中运行：

```powershell
winget install Hugo.Hugo.Extended
```

`winget` 是 Windows 11 自带的软件安装工具；`Hugo.Hugo.Extended` 表示安装扩展版 Hugo，兼容更多主题需求。

安装完成后，**关闭当前终端并新建一个 PowerShell 终端**，再运行：

```powershell
hugo version
```

你应该看到版本号，并包含 `extended` 字样。

如果没有看到：

1. 先确认已重新打开终端；
2. 再运行一次安装命令；
3. 如果提示找不到 `winget`，先在 Windows 设置中完成应用安装器更新后重试。

---

## 4. 创建本地 Hugo 项目

后续所有 Hugo 命令都要在项目根目录执行。为避免写死你的 Windows 用户名，本教程使用相对路径。

1. 在 VS Code 按 `Ctrl+K`、`Ctrl+O`，选择你的“文档”文件夹并打开。
2. 打开 **终端 → 新建终端**。
3. 运行：

```powershell
hugo new site my-hugo-blog
cd .\my-hugo-blog
code .
```

含义分别是：创建名为 `my-hugo-blog` 的站点、进入这个目录、让 VS Code 打开它。

此时左侧文件树会出现：

```text
my-hugo-blog/
├─ archetypes/
├─ assets/
├─ content/       ← 文章放这里
├─ data/
├─ i18n/
├─ layouts/
├─ static/        ← 图片等静态文件放这里
├─ themes/        ← 主题放这里
└─ hugo.toml      ← 网站总配置
```

> 你现在应该看到：VS Code 左下角已打开 `my-hugo-blog` 文件夹，终端路径以 `my-hugo-blog` 结尾。没有看到时，不要继续执行命令；先运行 `cd .\my-hugo-blog`。

---

## 5. 初始化 Git，并安装 PaperMod 主题

### 5.1 初始化 Git

仍在项目根目录时运行：

```powershell
git init -b main
```

这会让 Git 开始管理当前项目，并明确把主分支命名为 `main`。

首次使用 Git 的电脑还要设置提交署名：

```powershell
git config --global user.name "你的昵称"
git config --global user.email "你的 GitHub noreply 邮箱"
```

把双引号中的内容换成你自己的。`user.name` 可以是昵称；`user.email` 建议使用 GitHub Settings → Emails 中复制的 noreply 地址。

### 5.2 用 Git Submodule 安装 PaperMod

运行：

```powershell
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
```

这里的 `Submodule（子模块）` 可以简单理解为：你的博客项目记录“正在使用 PaperMod 的哪一版”，但不把主题的全部历史塞进自己的仓库。

执行成功后，应看到：

```text
themes/PaperMod/
.gitmodules
```

如果提示 `git` 找不到，回到第 3.2 节检查 Git；如果提示不在 Git 仓库中，先确认你执行过 `git init -b main` 且终端位于 `my-hugo-blog`。

### 5.3 写入最小网站配置

打开项目根目录的 `hugo.toml`，**全部替换**为下面内容：

```toml
baseURL = "https://你的项目名.pages.dev/"
languageCode = "zh-CN"
defaultContentLanguage = "zh"
title = "我的个人博客"
theme = "PaperMod"
timeZone = "Asia/Shanghai"

[[menus.main]]
  name = "文章"
  url = "/posts/"
  weight = 10
```

先把 `你的项目名` 临时保留；Cloudflare Pages 创建完成后，会得到真实地址，再回来替换它。

> 你现在应该看到：保存后没有红色报错；`themes/PaperMod` 文件夹存在。看不到主题文件夹时，不要只手动新建同名文件夹，重新运行上一节的子模块命令。

---

## 6. 用 Markdown 写第一篇文章，并测试本地图片

### 6.1 用 Hugo 创建文章骨架

在项目根目录运行：

```powershell
hugo new content posts/my-first-post.md
```

Hugo 会创建 `content/posts/my-first-post.md`，并自动填入日期、标题和 `draft = true`。

### 6.2 Markdown 最少要会什么

打开 `content/posts/my-first-post.md`，替换为以下内容。日期保持 Hugo 自动生成的值即可。

```toml
+++
title = "我的第一篇博客"
date = 2026-08-29T00:00:00+08:00
draft = false
+++

欢迎来到我的个人博客。这是我用 Hugo、GitHub 和 Cloudflare Pages 发布的第一篇文章。

## 我为什么开始写博客

我想把学习过程和思考记录下来，也希望以后能方便地继续更新。

更多信息可以访问 [Hugo 官网](https://gohugo.io/)。

![一张本地测试图片](/images/你的图片文件名.后缀)
```


上面分别演示了：普通段落、二级标题、链接和图片。

最重要的是把 `draft = false` 保留为 `false`。草稿为 `true` 时，正式构建不会发布这篇文章。

### 6.3 放入自己的本地图片

1. 在 `static` 文件夹内新建 `images` 文件夹。
2. 把你自己有权公开的任意格式图片复制到 `static/images/`，例如 `my-photo.webp` 或 `test.jpg`。
3. 修改文章中的图片行。例如图片名为 `my-photo.webp`，就写：

```markdown
![一张本地测试图片](/images/my-photo.webp)
```
![这是一个本地图片测试](/images/IMG_20251208_100123.jpg)

图片实际存放在 `static/images/my-photo.webp`，发布后访问地址会是 `https://你的域名/images/my-photo.webp`。这就是“本地图片随博客一起发布”。

> 你现在应该看到：图片路径以 `/images/` 开头，文件确实在 `static/images/` 中。图片不显示时，优先检查文件名、后缀和大小写是否完全一致。

### 6.4 本地预览

运行：

```powershell
hugo server -D
```

终端会显示一个本地网址，通常是 `http://localhost:1313/`。按住 `Ctrl` 点击它，或复制到浏览器打开。

你应该看到博客标题、文章列表、文章正文和测试图片。修改 Markdown 后保存，浏览器会自动刷新。

完成检查后，在终端按 `Ctrl+C` 停止本地服务器。

常见问题：

- 页面没有文章：检查文章是否在 `content/posts/`，以及本地预览是否用了 `-D`；
- 正文没有图片：检查图片是否在 `static/images/`，不是 `content/images/`；
- 终端提示主题找不到：检查 `theme = "PaperMod"` 的大小写与目录 `themes/PaperMod` 一致。

---

## 7. 第一次正式构建

本地预览会显示草稿；正式上线前，先运行一次真实构建：

```powershell
hugo
```

成功后项目根目录会出现 `public` 文件夹。这是 Hugo 生成的网站成品。

Cloudflare Pages 会自行生成这个文件夹，因此不要把 `public` 上传到 GitHub。创建根目录 `.gitignore` 文件，填入：

```gitignore
public/
resources/
.hugo_build.lock
```

> 你现在应该看到：`public` 已生成，且其中有 `index.html`。如果正式构建后文章消失，最常见原因是文章里的 `draft` 仍为 `true`。

---

## 8. 创建 GitHub 空仓库并首次推送

### 8.1 创建空仓库

1. 登录 GitHub，点击右上角 **+ → New repository（新建仓库）**。
2. Repository name 填 `my-hugo-blog`。如果你想换名字也可以，但后文所有同名位置都要一起替换。
3. 选择 **Public（公开）**。
4. **不要**勾选 README、`.gitignore` 或 License；我们本地已经有完整项目。
5. 点击 **Create repository**。



### 8.2 推送本地项目

回到 VS Code 的 PowerShell，确认还在项目根目录，然后依次执行：

```powershell
git add .
git status
git commit -m "首次发布我的 Hugo 博客"
git remote add origin https://github.com/你的GitHub用户名/my-hugo-blog.git
git push -u origin main
```

第四行的地址必须替换成 GitHub 新仓库页面显示的 HTTPS 地址。

首次 `git push` 时，Git Credential Manager 可能弹出浏览器要求登录 GitHub。按页面提示完成授权即可；不要手动创建或粘贴 Token。

刷新 GitHub 仓库页面后，应该能看到 `hugo.toml`、`content`、`static`、`themes` 和 `.gitmodules`。

常见问题：

- `remote origin already exists`：你已添加过远程地址，运行 `git remote -v` 核对后不要重复添加；
- `Authentication failed`：重新执行 `git push`，在弹出的浏览器中完成登录；
- 仓库缺少主题：确认 `.gitmodules` 和 `themes/PaperMod` 都已被 `git add .` 纳入提交。

---

## 9. 连接 Cloudflare Pages，让网站自动上线

### 9.1 导入 GitHub 仓库

1. 登录 Cloudflare 控制台，进入 **Workers & Pages**。
2. 点击 **Create application（创建应用）**，选择 **Pages**。
3. 选择 **Import an existing Git repository（导入现有 Git 仓库）**。
4. 按提示连接 GitHub。
5. 在 GitHub 授权页面选择 **Only select repositories（仅选择仓库）**，只授权 `my-hugo-blog`。
6. 回到 Cloudflare，选择这个仓库并点击 **Begin setup（开始设置）**。



### 9.2 填写构建设置

使用下面配置：

| 字段 | 填写内容 |
| --- | --- |
| Production branch | `main` |
| Framework preset | Hugo（若可选） |
| Build command | `hugo` |
| Build output directory | `public` |
| Root directory | 留空 |

Cloudflare Pages 的 Hugo 官方指南使用的也是 `hugo` 构建命令和 `public` 输出目录。

点击 **Save and Deploy（保存并部署）**，等待构建完成。



### 9.3 让 Cloudflare 与本地使用同一 Hugo 版本

构建成功后，打开项目的 **Settings → Environment variables**，新增：

| 名称 | 值 | 环境 |
| --- | --- | --- |
| `HUGO_VERSION` | 你的 `hugo version` 中的数字版本，例如 `0.160.1` | Production |

保存后，到 **Deployments** 重新部署最近一次构建。这样本地与 Cloudflare 会使用同一 Hugo 主版本，后续排错更简单。

> 你现在应该看到：部署状态为 Success，Cloudflare 给出一个 `https://某个项目名.pages.dev` 地址。构建失败时先打开日志，确认主题子模块和 Hugo 版本；不要盲目反复点击部署。

### 9.4 写入真实的 pages.dev 地址

把 Cloudflare 分配的网址复制下来，回到 `hugo.toml`，把：

```toml
baseURL = "https://你的项目名.pages.dev/"
```

改成真实地址，例如：

```toml
baseURL = "https://my-hugo-blog.pages.dev/"
```

然后运行：

```powershell
git add hugo.toml
git commit -m "设置 Pages 网站地址"
git push
```

等待下一次部署成功，打开 `pages.dev` 地址检查文章和图片。

Cloudflare 也会为非 `main` 分支提供预览部署，但本文不要求创建测试分支；日常发布前先用 `hugo server -D` 本地预览即可。

---

## 10. 以后怎样发布新文章

以后每次写文章，固定执行以下流程：

```powershell
# 1. 在项目根目录创建文章
hugo new content posts/文章文件名.md

# 2. 在 VS Code 编辑文章；准备发布时设为 draft = false

# 3. 本地预览
hugo server -D

# 4. 停止预览后，提交并推送
git add .
git commit -m "发布：文章标题"
git push
```

然后去 Cloudflare Pages 的 **Deployments** 看最新部署是否成功。默认情况下，仓库任意文件变化都会触发 Pages 构建；`main` 是你的正式站点来源。

> 建议：一次只完成一小块修改就提交一次。提交信息写清楚“发布什么”或“修复什么”，未来自己回看会非常轻松。

---

## 11. 换电脑或重装系统后如何恢复博客

先按本文安装 Git、Hugo Extended 和 VS Code，然后在你想保存项目的文件夹打开 PowerShell，运行：

```powershell
git clone --recurse-submodules https://github.com/你的GitHub用户名/my-hugo-blog.git
cd .\my-hugo-blog
code .
```

如果以前忘记使用 `--recurse-submodules`，进入项目后补运行：

```powershell
git submodule update --init --recursive
```

最后运行 `hugo server -D`。能打开本地网站，就说明源码、文章和 PaperMod 主题都已恢复。

---

## 12. 可选：购买 `.com` 并绑定自定义域名

这一章不影响 `pages.dev` 博客的正常使用。请先确认第 9 节已经成功上线。

### 12.1 选择一个适合长期使用的 `.com`

优先选择：短、好拼写、便于朗读、与个人长期身份相关的英文或拼音组合，例如：

```text
yourname.com
yourname-notes.com
```

避免：难记数字、易混淆拼写、他人商标、很长的连字符组合。Cloudflare Registrar 不支持 Unicode/中文域名注册，因此本教程只选择普通 ASCII 字符的 `.com`。

### 12.2 在 Cloudflare Registrar 购买

1. 在 Cloudflare 控制台打开 **Domain Registration / Register domains（注册域名）**。
2. 搜索你想要的 `.com`，确认可用性和当日价格。
3. 选择购买年限；先买 1 年即可。
4. 用真实且可收信的 ASCII 联系资料填写注册人信息。
5. 添加有效付款方式，核对价格、续费和条款后完成购买。
6. 检查注册邮箱的验证邮件并完成验证。



Cloudflare Registrar 会使用 Cloudflare 的名称服务器。建议长期博客保留自动续费，同时在日历中创建一条域名到期前 30 天的提醒。域名购买成功后通常不可退款，提交订单前务必再次核对拼写。

### 12.3 把根域名绑定到 Pages

1. 打开 **Workers & Pages → 你的 Pages 项目 → Custom domains（自定义域）**。
2. 点击 **Set up a domain（设置域名）**。
3. 输入根域名，例如 `example.com`，继续并确认。
4. 等待状态变为 Active。



通过 Cloudflare Registrar 购买的域名已在同一个 Cloudflare 账户中，通常不需要手动改名称服务器。Pages 激活根域名时会创建所需 DNS 记录并签发 HTTPS 证书。

激活后，回到 `hugo.toml`，将 `baseURL` 改为：

```toml
baseURL = "https://example.com/"
```

保存并推送：

```powershell
git add hugo.toml
git commit -m "绑定自定义域名"
git push
```

### 12.4 让 `www` 自动跳转到根域名

这里的目标是只保留一个正式网址：`https://example.com`。输入 `https://www.example.com/任意路径` 时，自动 301 跳转到没有 `www` 的同一路径。

1. 打开该域名的 **DNS → Records（DNS → 记录）**，新建一条记录：

   | 类型 | 名称 | IPv4 地址 | 代理状态 |
   | --- | --- | --- | --- |
   | A | `www` | `192.0.2.1` | 已代理（橙色云） |

   这个保留地址不会承载网站；Cloudflare 会先执行跳转规则。

2. 打开 **Rules → Bulk Redirects（批量重定向）**，创建一个列表，添加：

   | 来源 URL | 目标 URL | 状态 |
   | --- | --- | --- |
   | `www.example.com` | `https://example.com` | `301` |

   开启保留查询参数、子路径匹配和保留路径后缀。

3. 用这个列表创建并启用一条 Bulk Redirect 规则。
4. 在浏览器访问 `https://www.example.com/` 和 `https://www.example.com/posts/`，确认地址栏分别变成 `https://example.com/` 与 `https://example.com/posts/`。



如果域名一直显示 Pending：先检查注册邮箱验证是否完成、根域名是否已添加到 Pages、DNS 记录是否被错误修改。不要同时配置“根域名跳到 www”和“www 跳到根域名”，否则会形成循环跳转。

---

## 13. 常见错误集中排查

| 现象 | 优先检查 |
| --- | --- |
| `hugo` 不是命令 | 重开 VS Code 终端；确认运行过 `winget install Hugo.Hugo.Extended` |
| Hugo 提示找不到 `PaperMod` | `themes/PaperMod` 是否存在；`hugo.toml` 的主题名大小写是否一致 |
| 本地有文章，线上没有 | 文章的 `draft` 是否为 `false`；是否已 `git push`；Pages 最新部署是否 Success |
| 图片不显示 | 图片是否位于 `static/images/`；Markdown 路径是否为 `/images/文件名.后缀`；文件名大小写是否一致 |
| `git push` 认证失败 | 再执行一次 `git push`，在浏览器完成 GitHub 登录；检查 remote 地址是否属于你的仓库 |
| Pages 构建找不到主题 | GitHub 仓库是否有 `.gitmodules`；该文件是否同时包含 `path` 和 `url`；重新推送后查看构建日志 |
| 本地能构建、Cloudflare 失败 | 在 Pages 环境变量中把 `HUGO_VERSION` 设为本机 `hugo version` 的数字版本；检查构建命令为 `hugo`、输出目录为 `public` |
| 域名不能访问 | 完成邮箱验证；等待 Pages 自定义域状态 Active；检查是否错误删除 Pages 自动创建的 DNS 记录 |
| `www` 不跳转或循环跳转 | 确认只有 `www → 根域名` 一条规则；`www` A 记录必须是已代理状态 |

---

## 14. 你已经完成了什么

你现在拥有：

- 一个由 Hugo 生成的静态博客；
- 一份在 GitHub 公开保存的博客源码；
- 一个由 Cloudflare Pages 自动构建的 HTTPS 网站；
- 一套可重复的日常发布流程；
- 可选的 `.com` 自定义域名，以及统一的根域名入口；
- 即使换电脑，也能从 GitHub 恢复的博客项目。

先稳定写几篇文章，再考虑评论、搜索、统计、SEO、图床或更复杂的主题定制。第一次博客最重要的不是功能多，而是你能持续、安心地更新它。

## 官方资料

- [Hugo Quick Start](https://gohugo.io/getting-started/quick-start/)
- [Hugo：创建内容](https://gohugo.io/content-management/archetypes/)
- [PaperMod 安装说明](https://github.com/adityatelange/hugo-PaperMod/wiki/Installation)
- [Cloudflare Pages：部署 Hugo](https://developers.cloudflare.com/pages/framework-guides/deploy-a-hugo-site/)
- [Cloudflare Pages：自定义域名](https://developers.cloudflare.com/pages/configuration/custom-domains/)
- [Cloudflare：www 跳转到根域名](https://developers.cloudflare.com/pages/how-to/www-redirect/)
- [Cloudflare Registrar：注册域名](https://developers.cloudflare.com/registrar/get-started/register-domain/)


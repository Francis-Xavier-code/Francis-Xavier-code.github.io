<div align="center">

<img src="static/img/avatar.png" width="120" height="120" alt="avatar" style="border-radius:50%" />

# ✨ XYNRIN-BLOG

### *xynrin 的个人博客 · 一个安静记录的小角落*

<p>
  <img alt="Hugo" src="https://img.shields.io/badge/Hugo-extended_v0.161-FF4088?logo=hugo&logoColor=white&style=for-the-badge" />
  <img alt="Theme" src="https://img.shields.io/badge/Theme-Stack_v4-1f6feb?style=for-the-badge" />
  <img alt="License" src="https://img.shields.io/badge/License-GPL_v3-blue?style=for-the-badge&logo=gnu" />
  <img alt="Deploy" src="https://img.shields.io/badge/Deploy-GitHub_Pages-181717?style=for-the-badge&logo=github" />
</p>

<p>
  <img alt="GitHub Workflow" src="https://github.com/Xynrin/Xynrin.github.io/actions/workflows/hugo.yml/badge.svg" />
  <img alt="Last commit" src="https://img.shields.io/github/last-commit/Xynrin/Xynrin.github.io?style=flat-square" />
  <img alt="Repo size" src="https://img.shields.io/github/repo-size/Xynrin/Xynrin.github.io?style=flat-square" />
</p>

[🌐 Live Site](https://xynrin.github.io) · [📝 写文章](https://app.pagescms.org) · [🐧 Linux.do](https://linux.do/u/xynrin/) · [✉ Email](mailto:xynrin@163.com)

---

</div>

## 🌟 关于本站

> 不喧哗，自有声。
>
> 这里记录我在 **代码 / 学习 / 折腾 / 生活** 中遇到的一切。

```text
   __  ___   ___  _ _____  ___  ____  __
   \ \/ / \_/ / |/ |  ___|/ _ \|  _ \|  |
    \  / \   /| ' /| |__ | |_| | |_) |  |
    /  \  | | |  / |  __||  _  |  _ <|__|
   /_/\_\ |_| |_|\_|_|   |_| |_|_| \_|__|
```

## ✨ 站点特性

| 模块 | 实现 |
| :--- | :--- |
| 🚀 静态生成 | Hugo extended v0.161+ |
| 🎨 主题 | [hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack) v4 |
| ☁ 部署 | GitHub Actions → GitHub Pages（自动） |
| 📝 后台 | [Pages CMS](https://pagescms.org) 网页可视化编辑 |
| 🔍 搜索 | 主题内置全文搜索（JSON 索引） |
| 🌗 主题切换 | 跟随系统 / 手动切换 |
| 📡 RSS | 全文订阅 |
| 🌐 i18n | 中文（locale: zh-cn） |

## 🛠 本地开发

```bash
# 克隆（带 submodule）
git clone --recurse-submodules https://github.com/Xynrin/Xynrin.github.io.git
cd Xynrin.github.io

# 启动本地预览（默认 1313）
hugo server --buildDrafts

# 新建一篇文章
hugo new content post/your-post-name/index.md
```

## ☁ 自动部署流程

```mermaid
graph LR
    A[本地 / Pages CMS] -->|push to main| B[GitHub Repo]
    B --> C[GitHub Actions<br/>hugo build]
    C --> D[Upload Artifact]
    D --> E[Deploy to Pages]
    E --> F[xynrin.github.io]
```

## 📂 目录结构

```
.
├── .github/workflows/   # GitHub Actions 部署工作流
├── archetypes/          # 文章模板
├── assets/              # 经 Hugo 处理的资源（头像/banner/样式）
│   ├── icons/           # 自定义 SVG 图标
│   ├── img/             # 图片资源
│   └── scss/custom.scss # 自定义样式
├── content/             # 所有文章和页面
│   ├── about/           # 关于页
│   ├── post/            # 文章
│   ├── archives/        # 归档页
│   └── search.md        # 搜索页
├── layouts/             # 自定义模板（覆盖主题）
├── static/              # 原样复制的静态文件
├── themes/hugo-theme-stack/  # 主题（git submodule）
├── .pages.yml           # Pages CMS 配置
├── hugo.yaml            # Hugo 配置
└── LICENSE              # GPL-3.0
```

## 📜 License

本仓库**源码部分**采用 [GNU General Public License v3.0](./LICENSE) 协议开源。

**文章内容**采用 [知识共享 署名-非商业性使用-相同方式共享 4.0 国际许可协议（CC BY-NC-SA 4.0）](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh) 授权。

<div align="center">

---

<sub>Made with ❤ by <a href="https://github.com/Xynrin">xynrin</a> · 写于一个普通的下午</sub>

</div>

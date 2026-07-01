# 🔧 维护文档

> 日常维护需要点哪些网站、做哪些事，全在这里。

## 🗓 例行维护清单

### 每周（5 分钟）
- [ ] 检查 [GitHub Actions](https://github.com/Xynrin/Xynrin.github.io/actions) 有没有红色失败
- [ ] 翻一下 [仓库 Discussions](https://github.com/Xynrin/Xynrin.github.io/discussions) 看有没有新评论 / 不当内容

### 每月（15 分钟）
- [ ] `cd themes/PaperMod && git pull && cd ../..` 升级主题，本地 `hugo server` 看有没有破坏样式
- [ ] 跑 `hugo --gc` 清理失效缓存
- [ ] 查看 [Hugo 新版本](https://github.com/gohugoio/hugo/releases)，如有大版本更新，调整 `.github/workflows/hugo.yml` 里的 `HUGO_VERSION`

### 每年
- [ ] 备份评论数据：`gh api repos/Xynrin/Xynrin.github.io/discussions --paginate > discussions-backup.json`
- [ ] 看是否要换或加新的 logo / banner / 头像

---

## 🌐 第三方账号一览

平时只需要登 4 个网站：

| 网站 | 登录方式 | 用来做什么 |
|------|----------|------------|
| [GitHub](https://github.com/Xynrin) | 你的 GitHub 账号 | 改代码、看 Actions、看 Discussions 评论 |
| [Pages CMS](https://app.pagescms.org) | GitHub OAuth | 网页写文章 |
| [Giscus](https://giscus.app) | 不用登录 | 改评论配置（一次性，平时不用动） |
| [Linux.do](https://linux.do/u/xynrin/) | 你的 Linux.do 账号 | 社区互动 |

可选（出问题才登）：

| 网站 | 用途 |
|------|------|
| https://github.com/Xynrin/Xynrin.github.io/settings | 启用 Discussions / Pages 设置 |
| https://github.com/apps/giscus | Giscus App 配置 |
| https://giscus.app | Giscus ID 生成器 |
| https://busuanzi.ibruce.info/ | 不蒜子（基本不用动） |
| https://app.pagescms.org/Xynrin/Xynrin.github.io | 直达 Pages CMS 项目页 |

---

## 📝 写一篇新文章（最常用流程）

### 方式 A：Pages CMS 网页写（推荐）

1. 打开 https://app.pagescms.org
2. 选 `Xynrin.github.io` → 「文章」
3. 点「新建」
4. 填标题、分类、标签、正文（富文本编辑器，支持 Markdown）
5. 点「保存」→ 自动 commit + 推送 + 部署，1-2 分钟后上线

### 方式 B：本地写

```bash
hugo new content post/我的新文章/index.md
# 编辑 content/post/我的新文章/index.md
hugo server --buildDrafts   # 本地预览 http://localhost:1313

git add .
git commit -m "post: 我的新文章"
git push
```

### Front Matter 字段

```yaml
---
title: "文章标题"
date: 2026-05-19
slug: "url-slug"            # 决定文章 URL: /p/url-slug/
description: "摘要文字"
image: ""                    # 封面图（可空）
categories:
  - 随笔
tags:
  - 标签1
draft: false                 # 草稿不显示
reward: false                # 不显示打赏（默认显示）
comments: false              # 关闭评论（默认开启）
toc: false                   # 不显示目录（默认显示）
---
```

---

## 🎨 改样式

所有自定义样式集中在 `assets/scss/custom.scss`。

```bash
hugo server   # 改完会热更新
```

常用变量（在文件头部）：

```scss
:root {
  --accent-color: #00b8d4;       // 主色
  --gradient-accent: linear-gradient(135deg, #00d9ff, #ff2d92);  // 渐变色
}
```

---

## 🛠 改配置

`hugo.yaml` 是大本营。最常改的几块：

```yaml
title: XYNRIN-BLOG          # 站点标题

params:
  sidebar:
    subtitle: xynrin的个人博客
    avatar: img/avatar.png

  hero:
    enabled: true
    title: '...'
    subtitle: '...'
    typing:                 # 打字机循环句
      - "..."

  footer:
    customText: '...'

menu:
  social:                   # 社交链接
    - identifier: github
      url: https://github.com/Xynrin
```

---

## 🚨 应急：评论系统挂了

**症状**：文章页底部没出现评论区 / 评论提交失败。

**排查**：

1. 打开 https://github.com/Xynrin/Xynrin.github.io/settings → Features，确认 Discussions 勾着
2. 打开 https://github.com/apps/giscus → Configure，确认 App 装在 `Xynrin.github.io`
3. 打开任意一篇文章 F12 → Console，看有没有 giscus 相关红字报错
4. 报错 "Discussion not found" 是正常的：说明这篇文章还没有人评论，第一条评论会自动创建 Discussion
5. 报错 "App not installed" → 重新装 Giscus App
6. 想换 ID（比如换 category）→ 去 https://giscus.app 重新生成，更新 `hugo.yaml`

---

## 📦 备份

只要 GitHub 仓库还在，理论上你不需要备份。但建议每年一次：

```bash
# 备份博客本体（含所有评论数据：Discussions 用 GitHub API 导出）
git clone --mirror https://github.com/Xynrin/Xynrin.github.io.git
```

把 `.git` 文件夹存到 OneDrive / 网盘任何地方。

> 评论数据在仓库的 Discussions 里，跟代码不在同一棵 git 树上。要单独备份评论的话用：
> ```bash
> gh api repos/Xynrin/Xynrin.github.io/discussions --paginate > discussions-backup.json
> ```

---

## ❓ 你忘记了某个网站？查这表

| 我想… | 去哪 |
|-------|------|
| 写文章 | https://app.pagescms.org |
| 看部署状态 | https://github.com/Xynrin/Xynrin.github.io/actions |
| 看评论 | https://github.com/Xynrin/Xynrin.github.io/discussions |
| 改评论配置 | https://giscus.app |
| 看主题最新版 | https://github.com/adityatelange/hugo-PaperMod/releases |
| 看 Hugo 最新版 | https://github.com/gohugoio/hugo/releases |

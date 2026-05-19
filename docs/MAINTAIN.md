# 🔧 维护文档

> 日常维护需要点哪些网站、做哪些事，全在这里。

## 🗓 例行维护清单

### 每周（5 分钟）
- [ ] 检查 [GitHub Actions](https://github.com/Xynrin/Xynrin.github.io/actions) 有没有红色失败
- [ ] 看一眼 [Vercel Deployments](https://vercel.com/dashboard)，确保 `pinglun-blog` 是绿色 Ready
- [ ] 翻一下 [waline-data](https://github.com/Xynrin/waline-data) 仓库 commits，看有没有评论 / 垃圾评论

### 每月（15 分钟）
- [ ] `cd themes/hugo-theme-stack && git pull && cd ../..` 升级主题，本地 `hugo server` 看有没有破坏样式
- [ ] 跑 `hugo --gc` 清理失效缓存
- [ ] 查看 [Hugo 新版本](https://github.com/gohugoio/hugo/releases)，如有大版本更新，调整 `.github/workflows/hugo.yml` 里的 `HUGO_VERSION`
- [ ] 检查 GitHub Token 是否还有效（你设置的是 No expiration 就免操心）

### 每年
- [ ] 备份 `waline-data` 仓库（评论数据，简单 `git clone` 一份）
- [ ] 看是否要换或加新的 logo / banner / 头像

---

## 🌐 第三方账号一览

平时只需要登 4 个网站：

| 网站 | 登录方式 | 用来做什么 |
|------|----------|------------|
| [GitHub](https://github.com/Xynrin) | 你的 GitHub 账号 | 改代码、看 Actions |
| [Pages CMS](https://app.pagescms.org) | GitHub OAuth | 网页写文章 |
| [Vercel](https://vercel.com/dashboard) | GitHub OAuth | 看评论后端状态、查日志 |
| [Linux.do](https://linux.do/u/xynrin/) | 你的 Linux.do 账号 | 社区互动 |

可选（出问题才登）：

| 网站 | 用途 |
|------|------|
| https://github.com/settings/tokens | 重新生成 Waline Token |
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

**症状**：访客提交评论失败 / 评论框白板。

**排查**：

1. 浏览器 F12 开 Network，刷文章页，找 `pinglun-blog.vercel.app` 请求看响应
2. 直接 `curl https://pinglun-blog.vercel.app/api/comment` 应该返回 `{"errno":1001,...}`（这是正常的）
3. 如果 500：去 [Vercel](https://vercel.com/dashboard) → `pinglun-blog` → Functions → 看错误日志
4. 如果是 GitHub Token 过期：
   - https://github.com/settings/tokens 生成新的（勾 `repo`）
   - Vercel → Settings → Environments → Production → 改 `GITHUB_TOKEN`
   - Deployments → Redeploy（不用 Build Cache）

---

## 📦 备份

只要 GitHub 仓库还在，理论上你不需要备份。但建议每年一次：

```bash
# 备份博客本体
git clone --mirror https://github.com/Xynrin/Xynrin.github.io.git
# 备份评论数据
git clone --mirror https://github.com/Xynrin/waline-data.git
```

把这两个 `.git` 文件夹存到 OneDrive / 网盘任何地方。

---

## ❓ 你忘记了某个网站？查这表

| 我想… | 去哪 |
|-------|------|
| 写文章 | https://app.pagescms.org |
| 看部署状态 | https://github.com/Xynrin/Xynrin.github.io/actions |
| 看评论后端 | https://vercel.com/dashboard |
| 看评论数据 | https://github.com/Xynrin/waline-data |
| 看主题最新版 | https://github.com/CaiJimmy/hugo-theme-stack/releases |
| 看 Hugo 最新版 | https://github.com/gohugoio/hugo/releases |
| 改 GitHub Token | https://github.com/settings/tokens |

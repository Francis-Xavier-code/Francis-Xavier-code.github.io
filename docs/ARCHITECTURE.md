# 🏗 原理 / 架构文档

> 这份文档讲清楚整个博客是怎么运转的。每一块用什么、为什么这么选、数据怎么流。

## 🎯 核心理念：静态站 + Serverless 数据层

GitHub Pages 只能托管静态文件，没有任何后端能力。但博客需要一些「动态」功能：评论、浏览量、点赞。
解决方案：**静态站负责展示，第三方 Serverless 负责数据**。

```
┌─────────────────────────────────────────────────────────┐
│                       浏览器                            │
│  ┌──────────────────┐    ┌──────────────────────────┐  │
│  │ Hugo 静态 HTML   │    │ JS 异步请求 Waline       │  │
│  │ (xynrin.github.io)│───▶│ (pinglun-blog.vercel.app)│  │
│  └──────────────────┘    └────────┬─────────────────┘  │
│                                    │ GitHub API         │
│                                    ▼                    │
│                          ┌──────────────────┐           │
│                          │ waline-data 仓库 │           │
│                          │ (JSON 文件存储)  │           │
│                          └──────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 技术栈分层

| 层 | 技术 | 选择理由 |
|----|------|----------|
| 静态生成 | Hugo extended | 单文件二进制、build 速度极快、SCSS 内置 |
| 主题 | hugo-theme-stack v4 | 设计干净、可定制度高、社区活跃 |
| 部署 | GitHub Pages + GitHub Actions | 免费、和代码托管同处、零配置 |
| 写作后台 | Pages CMS | 零自建、GitHub App 授权、可视化字段 |
| 评论后端 | Waline | 开源、UI 漂亮、点赞浏览量一体 |
| 评论部署 | Vercel | 免费 Serverless、国内速度尚可、和 GitHub 联动 |
| 评论数据 | GitHub Repo | 不依赖任何数据库服务、永久免费、可备份 |
| 全站统计 | 不蒜子 | 一行 JS 即可、零配置 |
| README 徽章 | shields.io / visitor-badge | 公开免费、实时数据 |

---

## 🌊 数据流详解

### 1. 写文章 → 上线

```
你（Pages CMS / 本地）
  ↓ 编辑 Markdown
Git commit + push to main
  ↓ 触发
GitHub Actions (.github/workflows/hugo.yml)
  ↓ 步骤
  ├─ Checkout（含 submodule 主题）
  ├─ Setup Pages
  ├─ hugo --gc --minify --baseURL ...
  ├─ Upload artifact (./public)
  └─ Deploy to Pages environment
  ↓
xynrin.github.io 更新（缓存约 1 分钟）
```

### 2. 访客看页面

```
浏览器请求 xynrin.github.io/p/xxx/
  ↓ GitHub Pages CDN 返回静态 HTML
浏览器解析 HTML，并行加载：
  ├─ Hugo 编译的 CSS / JS
  ├─ 不蒜子 JS（busuanzi.pure.mini.js）→ 写 PV/UV 到页脚
  └─ Waline JS（@waline/client）
       ↓ init({ serverURL: 'https://pinglun-blog.vercel.app' })
       ↓ AJAX 请求
       Vercel Serverless Function (Waline)
         ↓ 用 GITHUB_TOKEN 调 GitHub API
         读取 waline-data 仓库 comments/ 下的 JSON
         ↓
         返回评论数 / 浏览量
       ↓
       Waline 渲染评论框 + 浏览量数字
```

### 3. 访客提交评论

```
访客填评论 → 点提交
  ↓
Waline 前端 POST 到 pinglun-blog.vercel.app/api/comment
  ↓ Vercel 函数
  ↓ 反垃圾检查（SITE_URL 同源 + Akismet 默认启用）
  ↓ 用 GITHUB_TOKEN 通过 GitHub API
  ↓ 在 waline-data 仓库新建 / 更新 JSON
GitHub 收到 commit（commit 作者是 Waline 机器人）
  ↓ 评论入库
返回成功 → 前端自动刷新评论列表
```

### 4. 不蒜子统计

```
浏览器加载 busuanzi.pure.mini.js
  ↓ 自动上报 referer + 站点
不蒜子服务器记录 PV/UV
  ↓ 异步返回数字
JS 写到 #busuanzi_value_site_pv 和 #busuanzi_value_site_uv
  ↓
页脚显示
```

不蒜子**没有公开 API**，数据只能在网页 JS 里展示，README 不能直接读。

---

## 📁 项目结构

```
.
├── .github/workflows/hugo.yml       # 部署工作流
├── archetypes/default.md            # 新文章模板（hugo new 用）
├── assets/                          # Hugo 处理的资源（会被 build）
│   ├── icons/                       # 自定义 SVG 图标
│   ├── img/                         # 头像 / favicon / banner / 赞赏码
│   ├── scss/custom.scss             # 自定义样式入口
│   └── jsconfig.json                # 主题 JS 配置
├── content/                         # 所有页面与文章
│   ├── about/index.md               # 关于
│   ├── archives/_index.md           # 归档
│   ├── categories/_index.md         # 分类
│   ├── tags/_index.md               # 标签
│   ├── search.md                    # 搜索（layout: search）
│   └── post/                        # 文章
│       └── 文章 slug/index.md       # 单篇文章（连同图片同目录）
├── layouts/                         # 模板覆盖（优先级高于主题）
│   ├── 404.html                     # 故障霓虹 404
│   ├── home.html                    # 首页（含 Hero 区）
│   ├── single.html                  # 文章页（含返回 + 打赏 + 评论）
│   ├── index.json                   # 搜索 JSON 索引
│   ├── _partials/
│   │   ├── head/custom.html         # 不蒜子 / Waline / KaTeX 注入
│   │   ├── footer/
│   │   │   ├── footer.html          # 自定义页脚（运行时间 / PV / UV）
│   │   │   └── custom.html          # 进度条 / 回到顶部 / TOC / Mermaid / 快捷键
│   │   ├── sidebar/left.html        # 左栏（底部 banner + 灯箱）
│   │   ├── widget/rss-qr.html       # RSS 二维码 widget
│   │   ├── article/components/
│   │   │   ├── details.html         # 字数 / 阅读时长 / 浏览量
│   │   │   └── reward.html          # 打赏按钮
│   │   └── comments/provider/
│   │       └── waline.html          # Waline 接入
│   └── page/search.html             # fzf 风格搜索页
├── static/                          # 原样复制（不经 Hugo 处理）
│   ├── admin/                       # （Decap CMS 入口预留）
│   └── img/                         # 公共静态图
├── themes/hugo-theme-stack/         # 主题（Git submodule，别直接改）
├── docs/                            # 这个目录！
│   ├── DEPLOY.md
│   ├── MAINTAIN.md
│   └── ARCHITECTURE.md
├── .gitmodules                      # 主题 submodule
├── .gitignore
├── .pages.yml                       # Pages CMS 配置
├── hugo.yaml                        # 站点配置（最重要）
├── LICENSE                          # GPL-3.0
└── README.md                        # 项目门面
```

---

## 🧠 关键设计决策

### 为什么主题用 submodule 不直接复制？
- 升级方便：`cd themes/hugo-theme-stack && git pull` 即可
- 自己的修改全放 `layouts/` 和 `assets/scss/custom.scss`，不污染主题源码

### 为什么 search 用自研 fzf 不用 Algolia？
- Algolia 要注册账号、配 API key、有免费额度限制
- 自研脚本（`layouts/page/search.html`）压缩后 < 5KB，纯前端模糊匹配
- 索引文件 `index.json` 由 `layouts/index.json` 生成，文章正文截断 800 字防止过大

### 为什么不蒜子 PV 不能在 README 显示？
- 不蒜子工作机制：浏览器加载它的 JS 时上报，再由 JS 把数字写进页面
- **它没有公开 HTTP API** 让外部按用户名查询数字
- 想在 README 显示真实 PV，必须换用 Umami / Vercel Analytics 这类有 API 的服务

### 为什么 Waline 用 GitHub 当数据库不用 LeanCloud？
- LeanCloud 国内站对个人开发者关闭了新注册
- LeanCloud 国际站需要绑信用卡
- GitHub 仓库 + Token 完全免费、永不下线、想备份直接 clone

### 为什么 Vercel 不直接放在 GitHub Pages？
- GitHub Pages 是纯静态托管，不能跑 Node.js
- Waline 需要 Serverless Function 处理评论提交、调 GitHub API、反垃圾
- Vercel 提供免费 Serverless Function，且和 GitHub 联动好

---

## 🔐 安全模型

| 资源 | 保护方式 | 风险 |
|------|----------|------|
| 博客主仓库 | Public（必须公开） | 无敏感数据 |
| waline-data 仓库 | Private + Token | Token 泄漏 → 评论可被篡改 |
| Vercel 环境变量 | 加密存储 | 仅项目所有者可见 |
| GitHub Token | repo 权限、不过期 | 定期检查活动日志，疑似异常立即吊销 |
| Hugo 配置 | hugo.yaml 公开 | 无敏感字段（serverURL 是公开的） |

**绝对不能进 git 的东西**：
- GitHub Token（`ghp_xxx`）
- 任何含 `secret` / `private_key` 的字段

---

## 📚 阅读延伸

| 想深入… | 看这个 |
|---------|--------|
| Hugo 模板语法 | https://gohugo.io/templates/ |
| 主题文档 | https://stack.jimmycai.com/ |
| GitHub Actions | https://docs.github.com/actions |
| Waline 文档 | https://waline.js.org/ |
| Pages CMS 文档 | https://pagescms.org/docs |

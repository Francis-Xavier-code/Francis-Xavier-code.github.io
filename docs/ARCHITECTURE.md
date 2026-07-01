# 🏗 原理 / 架构文档

> 这份文档讲清楚整个博客是怎么运转的。每一块用什么、为什么这么选、数据怎么流。

## 🎯 核心理念：静态站 + 第三方数据层

GitHub Pages 只能托管静态文件，没有任何后端能力。但博客需要一些「动态」功能：评论、统计。
解决方案：**静态站负责展示，第三方服务负责数据**。

```
┌─────────────────────────────────────────────────────────┐
│                       浏览器                            │
│  ┌──────────────────┐    ┌──────────────────────────┐  │
│  │ Hugo 静态 HTML   │    │ Giscus iframe            │  │
│  │ (xynrin.github.io)│───▶│ (giscus.app)             │  │
│  └──────────────────┘    └────────┬─────────────────┘  │
│                                    │ GitHub GraphQL     │
│                                    ▼                    │
│                          ┌──────────────────┐           │
│                          │ 仓库 Discussions │           │
│                          └──────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 技术栈分层

| 层 | 技术 | 选择理由 |
|----|------|----------|
| 静态生成 | Hugo extended | 单文件二进制、build 速度极快、SCSS 内置 |
| 主题 | PaperMod | 设计干净、可定制度高、社区活跃 |
| 部署 | GitHub Pages + GitHub Actions | 免费、和代码托管同处、零配置 |
| 写作后台 | Pages CMS | 零自建、GitHub App 授权、可视化字段 |
| 文章评论 | Giscus | 零自建、用 GitHub Discussions 当数据库 |
| 瞬间评论 | Twikoo | 可选启用，支持匿名评论，未配置 envId 时自动隐藏 |
| 文章评论数据 | 仓库 Discussions | 不依赖外部服务、永久免费、自带反垃圾 |
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
  └─ Giscus iframe（giscus.app/client.js）
       ↓ 通过 pathname 找到对应的 Discussion
       ↓ 调 GitHub GraphQL API
       仓库 Discussions
       ↓
       渲染评论列表 + reactions
```

### 3. 访客提交文章评论

```
访客点击 Giscus 评论框 → 用 GitHub 登录授权
  ↓ Giscus 引导 OAuth 流程
GitHub 校验通过，发回 token
  ↓
Giscus 通过 GitHub API 在 Discussions 里新增 comment
GitHub 自动反垃圾 + 通知（你能在 GitHub 收到通知）
  ↓
评论实时显示
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
│   ├── partials/
│   │   ├── comments.html            # 文章 Giscus 评论
│   │   ├── memo-comments.html       # 瞬间 Twikoo 评论（可选）
│   │   ├── memo-lightbox.html       # 瞬间图片灯箱
│   │   ├── extend_head.html         # AdSense 等 head 扩展
│   │   ├── extend_post_content.html # 打赏 / 许可 / 广告位
│   │   └── footer.html              # 自定义页脚（运行时间 / PV / UV）
│   ├── memos/
│   │   ├── list.html                # 瞬间列表页
│   │   └── single.html              # 瞬间详情页
│   └── shortcodes/friends.html      # 友链短代码├── static/                          # 原样复制（不经 Hugo 处理）
│   ├── admin/                       # （Decap CMS 入口预留）
│   └── img/                         # 公共静态图
├── themes/PaperMod/         # 主题（Git submodule，别直接改）
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
- 升级方便：`cd themes/PaperMod && git pull` 即可
- 自己的修改全放 `layouts/` 和 `assets/scss/custom.scss`，不污染主题源码

### 为什么 search 用自研 fzf 不用 Algolia？
- Algolia 要注册账号、配 API key、有免费额度限制
- 自研脚本（`layouts/page/search.html`）压缩后 < 5KB，纯前端模糊匹配
- 索引文件 `index.json` 由 `layouts/index.json` 生成，文章正文截断 800 字防止过大

### 为什么不蒜子 PV 不能在 README 显示？
- 不蒜子工作机制：浏览器加载它的 JS 时上报，再由 JS 把数字写进页面
- **它没有公开 HTTP API** 让外部按用户名查询数字
- 想在 README 显示真实 PV，必须换用 Umami / Vercel Analytics 这类有 API 的服务

### 为什么文章评论选 Giscus，瞬间评论预留 Twikoo？
- Giscus 不需要后端，所有数据存在仓库的 Discussions 里，配 4 个 ID 就能用
- 文章评论用 Giscus，适合长文讨论；瞬间评论预留 Twikoo，适合匿名轻互动
- Twikoo 未配置 `params.twikoo.envId` 时不渲染评论区，不影响瞬间页面
- 代价：Giscus 访客必须有 GitHub 账号；Twikoo 需要你自行配置 CloudBase / Vercel / 私有服务
- 评论隐私？Giscus Discussion 是公开的，但你可以删任何 comment
---

## 🔐 安全模型

| 资源 | 保护方式 | 风险 |
|------|----------|------|
| 博客主仓库 | Public（必须公开） | 无敏感数据 |
| Discussions（评论） | 跟仓库一样公开 | 评论可被任何人看到（这是设计如此） |
| Hugo 配置 | hugo.yaml 公开 | 无敏感字段 |

**绝对不能进 git 的东西**：
- 任何含 `secret` / `private_key` 的字段
- 个人邮箱/手机号（在 markdown 文本里写没问题，URL 参数里别写）

---

## 📚 阅读延伸

| 想深入… | 看这个 |
|---------|--------|
| Hugo 模板语法 | https://gohugo.io/templates/ |
| 主题文档 | https://github.com/adityatelange/hugo-PaperMod/wiki/ |
| GitHub Actions | https://docs.github.com/actions |
| Giscus 文档 | https://github.com/giscus/giscus |
| Pages CMS 文档 | https://pagescms.org/docs |

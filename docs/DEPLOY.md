# 🚀 部署文档

> 这份文档记录从零到上线的完整部署流程。如果你（或未来的你）需要重建一遍博客，按这份走。

## 📋 一句话原理

`本地写 Markdown` → `git push 到 GitHub` → `GitHub Actions 自动 build Hugo` → `部署到 GitHub Pages` → `xynrin.github.io 更新`。

评论由 `Giscus`（基于 GitHub Discussions）处理，零自建后端。

---

## 🧰 本地环境

| 工具 | 版本 | 安装 |
|------|------|------|
| Hugo extended | v0.161+ | https://gohugo.io/installation/ |
| Git | any | https://git-scm.com |
| Node.js（可选） | LTS | https://nodejs.org （仅 Pages CMS 本地预览要） |

```bash
# 验证
hugo version          # 应输出 extended
git --version
```

---

## 🌐 一、GitHub 仓库

1. **博客主仓库**：`Xynrin/Xynrin.github.io`（Public，必须公开 Pages 才免费）
2. **文章评论数据**：`Xynrin/Xynrin.github.io` 仓库 Discussions（Giscus 使用）

启用 Pages：

- 打开 https://github.com/Xynrin/Xynrin.github.io/settings/pages
- **Build and deployment → Source → 选 GitHub Actions**（关键，默认是 "Deploy from branch"）

---

## 🧱 二、首次部署

```bash
# 克隆（带 submodule）
git clone --recurse-submodules https://github.com/Xynrin/Xynrin.github.io.git
cd Xynrin.github.io

# 本地预览
hugo server --buildDrafts
# 浏览器打开 http://localhost:1313
```

每次推送 main 分支，`.github/workflows/hugo.yml` 自动触发：

```mermaid
graph LR
    A[git push] --> B[GitHub Actions]
    B --> C[Hugo build extended]
    C --> D[Upload Pages artifact]
    D --> E[Deploy to Pages]
    E --> F[xynrin.github.io]
```

---

## 💬 三、评论系统（Giscus）

> 用 GitHub Discussions 当数据库，零自建后端。访客需要 GitHub 账号才能评论。

### 一次性配置

1. **启用仓库 Discussions**：https://github.com/Xynrin/Xynrin.github.io/settings → Features → 勾 Discussions
2. **安装 Giscus App**：https://github.com/apps/giscus → Install → 仅选 `Xynrin.github.io` 仓库
3. **生成 ID**：https://giscus.app → 输入仓库名验证 → 选 pathname / Announcements → 复制 4 个 ID

### `hugo.yaml` 配置

```yaml
params:
  comments:
    enabled: true
    provider: giscus
    giscus:
      repo: Xynrin/Xynrin.github.io
      repoID: R_kgDOSiCzDA               # giscus.app 验证后获取
      category: Announcements
      categoryID: DIC_kwDOSiCzDM4C9Z8_   # giscus.app 验证后获取
      mapping: pathname
      lightTheme: light
      darkTheme: dark_dimmed
      reactionsEnabled: 1
      inputPosition: top
      lang: zh-CN
      loading: lazy
```

> 评论数据存在仓库的 Discussions 里，每篇文章自动对应一个 Discussion。
> 瞬间页可选使用 Twikoo：在 `hugo.yaml` 的 `params.twikoo.envId` 填入 CloudBase 环境 ID 或服务 URL 后启用。

---

## 📝 四、写文章

### 方式 A：本地写

```bash
hugo new content post/your-post-slug/index.md
# 编辑文件后
hugo server --buildDrafts   # 本地预览
git add .
git commit -m "post: 你的标题"
git push
```

### 方式 B：网页 CMS

- 打开 https://app.pagescms.org
- 用 GitHub 登录授权（首次会让你装 Pages CMS App 到仓库）
- 选 `Xynrin.github.io` → 「文章」面板 → 新建
- 保存即自动 commit + 部署

### 方式 C：GitHub 网页

- 直接到仓库 `content/post/` 编辑或新建文件，commit 即触发部署

---

## 📊 五、统计与第三方服务总览

| 服务 | 用途 | 后台地址 | 备注 |
|------|------|----------|------|
| GitHub | 代码 + Pages 托管 | https://github.com/Xynrin | 主战场 |
| Pages CMS | 网页可视化写文章 | https://app.pagescms.org | 用 GitHub 登录 |
| Giscus | 评论系统 | https://giscus.app | 数据存仓库 Discussions，零后端 |
| 不蒜子 | 全站 PV/UV | （无后台，自动统计） | https://busuanzi.ibruce.info |
| visitor-badge | README 浏览徽章 | https://visitor-badge.laobi.icu | 公开服务 |
| shields.io | GitHub 数据徽章 | https://shields.io | 公开服务 |
| capsule-render | Profile banner 横幅 | https://capsule-render.vercel.app | 公开服务 |

---

## 🔁 六、常见操作清单

| 想做什么 | 在哪做 |
|----------|--------|
| 改主题颜色 / 样式 | `assets/scss/custom.scss` |
| 改标题 / 副标题 / 头像 | `hugo.yaml` 的 `params.sidebar` |
| 加 / 删 社交链接 | `hugo.yaml` 的 `menu.social` |
| 改 footer 文字 | `hugo.yaml` 的 `params.footer.customText` |
| 改 banner 图 | 替换 `assets/img/my-linux-do.png` |
| 改 favicon | 替换 `assets/img/favicon.png` |
| 改赞赏码 | 替换 `assets/img/zan-shang.png` |
| 改 Hero 大标语 | `hugo.yaml` 的 `params.hero` |
| 升级主题 | `cd themes/PaperMod && git pull` |

---

## 🧯 七、故障速查

| 现象 | 检查 |
|------|------|
| 网站访问 404 | Settings → Pages → Source 必须是 GitHub Actions |
| 部署成功但页面没更新 | 浏览器强刷 `Ctrl + F5` |
| 评论框不显示 | 1. 仓库 Discussions 是否启用；2. Giscus App 是否装到这个仓库；3. `hugo.yaml` 里的 `repoID` / `categoryID` 是否正确 |
| 评论提交报错 "App not installed" | 去 https://github.com/apps/giscus 重新装到仓库 |
| 不蒜子数字一直是 0 | 该服务偶尔不稳定，等几小时再看 |
| 中文徽章乱码 | shields.io 的 URL 参数里别用中文，用纯英文 |

如果整个 GitHub Actions 部署失败：去 https://github.com/Xynrin/Xynrin.github.io/actions 看 log，常见原因是 hugo.yaml 改坏了 YAML 缩进。

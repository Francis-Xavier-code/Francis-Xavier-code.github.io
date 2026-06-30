---
title: "Changelog"
type: "page"
comments: false
ShowReadingTime: false
ShowWordCount: true
ShowPostNavLinks: false
---

记录本网站的版本更新与变动

如果你希望此博客需要添加一些功能，请提交 [issue](https://github.com/Xynrin/Xynrin.github.io/issues)

---

## 2026-06-30

### 新增
- 添加文章内超链接在新建标签页中打开
- 新建“朋友们”栏目及自定义友链卡片组件，包含 [朋友列表](/friends/) 与 [交换友链说明](/friends/make-a-friend/) 页面
- 在主导航栏中增加了“朋友”菜单入口

### 变更
- 重构 Giscus 评论区，启用 `transparent_dark` 半透明主题，使其与暗黑模式固定背景无缝融合

### 修复
- 修复因动态加载导致的 Giscus 评论区连接请求被拒绝问题，改回静态 HTML 引入以确保稳定性


## 2026-06-22

### 变更
- 更换主题为 **[Hugo PaperMod](https://themes.gohugo.io/themes/hugo-papermod/)**，拥有更极简的阅读体验。
- 重构主页为 **个人名片模式 (Profile Mode)**。
- 全站本地图片路径重构，支持在本地 Markdown 编辑器内直接肉眼预览图片。

### 修复
- 修复并保留了不蒜子访问量统计和运行时长统计。


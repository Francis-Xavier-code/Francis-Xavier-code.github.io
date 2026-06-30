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
- 新增文章底部“版权声明卡片”（CC BY-NC-SA 4.0 协议），规范文章授权保护
- 全新设计并开发了“本地网页管理后台（Xynrin Admin）”，提供可视化的文章管理（支持联动唤起 Typora）、朋友圈瞬间发布（支持图片多选/拖拽自动上传处理）以及一键同步部署
- 瞬间栏目新增“大图灯箱预览（Lightbox）”功能，支持多图轮播与键盘交互切换
- 瞬间栏目主页增加“独立评论与点赞”按钮，并为瞬间创建专属的详情展示与 Giscus 表情回应系统

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


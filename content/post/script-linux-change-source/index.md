---
title: "linux快速换源"
date: 2026-06-22
slug: "script-linux-change-source"
description: "linux快速换源脚本，支持在线使用"
categories:
  - 随笔
tags:
  - linux
  - 脚本
  - script
  - 工具
draft: false
---

# 脚本说明

## 1. 脚本适配范围

| 操作系统                                                     | 适配版本                  |
| :----------------------------------------------------------- | :------------------------ |
| <img src="https://img.shields.io/badge/-Debian-red?style=flat&logo=debian&logoColor=white" height="20" style="vertical-align: middle;"> | 8～13                     |
| <img src="https://img.shields.io/badge/-Ubuntu-E95420?style=flat&logo=ubuntu&logoColor=white" height="20" style="vertical-align: middle;"> | 14～26                    |
| <img src="https://img.shields.io/badge/-Kali_Linux-white?style=flat&logo=kali-linux&logoColor=5575F5" height="20" style="vertical-align: middle;"> | all                       |
| <img src="https://img.shields.io/badge/-Linux_Mint-96C93D?style=flat&logo=linux-mint&logoColor=white" height="20" style="vertical-align: middle;"> | 17～22 / LMDE 2～7        |
| <img src="https://img.shields.io/badge/-RHEL-CC0000?style=flat&logo=red-hat&logoColor=white" height="20" style="vertical-align: middle;"> | 7～10                     |
| <img src="https://img.shields.io/badge/-Fedora-3C50B0?style=flat&logo=fedora&logoColor=white" height="20" style="vertical-align: middle;"> | 30～44                    |
| <img src="https://img.shields.io/badge/-CentOS-262577?style=flat&logo=centos&logoColor=white" height="20" style="vertical-align: middle;"> | 7～8 / Stream 8～10       |
| <img src="https://img.shields.io/badge/-Arch_Linux-1793D1?style=flat&logo=arch-linux&logoColor=white" height="20" style="vertical-align: middle;"> | all                       |
| <img src="https://img.shields.io/badge/-openSUSE-73BA25?style=flat&logo=opensuse&logoColor=white" height="20" style="vertical-align: middle;"> | Leap 15 ~ 16 / Tumbleweed |

---

## 2. 换源在线脚本

```bash
bash <(curl -sSL https://linuxmirrors.cn/main.sh)
```

ps: 终端必须使用bash,并且在`ROOT`环境下运行  

---

## 3. 输出预览

```bash
 请选择你想使用的软件源：

➤ 阿里云
  腾讯云
  华为云
  移动云
  天翼云
  网易
  火山引擎
  清华大学
  北京大学
  浙江大学
  南京大学
  兰州大学
  上海交通大学
  华中科技大学
  中国科学技术大学
  中国科学院软件研究所
  中国科技云
  官方源


```

```bash
+-----------------------------------+
| ⡇  ⠄ ⣀⡀ ⡀⢀ ⡀⢀ ⡷⢾ ⠄ ⡀⣀ ⡀⣀ ⢀⡀ ⡀⣀ ⢀⣀ |
| ⠧⠤ ⠇ ⠇⠸ ⠣⠼ ⠜⠣ ⠇⠸ ⠇ ⠏  ⠏  ⠣⠜ ⠏  ⠭⠕ |
+-----------------------------------+
欢迎使用 GNU/Linux 更换系统软件源脚本

运行环境 Ubuntu 24.04.4 LTS x86_64
系统时间 2026-06-04 14:12 Asia/Shanghai

➜  腾讯云

╭─ 请选择软件源的网络地址(访问方式)：
│
╰─ ● 公网 / ○ 内网

╭─ 请选择软件源网络协议：
│
╰─ ● HTTP / ○ HTTPS

'/etc/apt/sources.list.d/ubuntu.sources' -> '/etc/apt/sources.list.d/ubuntu.sources.bak'

✔ 已备份原有 ubuntu.sources 源文件
```

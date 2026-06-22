import os
import subprocess
import datetime
import urllib.request
import json
import time
import sys

os.system("color")

C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_BLUE = '\033[94m'
C_CYAN = '\033[96m'
C_RED = '\033[91m'
C_RESET = '\033[0m'
C_BOLD = '\033[1m'

def print_header(title):
    print(f"\n{C_CYAN}{C_BOLD}=== {title} ==={C_RESET}\n")

def print_step(msg):
    print(f"{C_BLUE}•{C_RESET} {msg}")

def print_success(msg):
    print(f"{C_GREEN}✔{C_RESET} {msg}")

def print_error(msg):
    print(f"{C_RED}✖{C_RESET} {msg}")

print_header("🚀 Xynrin's Blog - 一键发布部署 🚀")

print_step("正在分析本地文件变更...")
res = subprocess.run(["git", "add", "."], capture_output=True)
if res.returncode != 0:
    print_error("Git add 失败！")
    print(res.stderr.decode('utf-8', errors='replace'))
    input("\n按回车键退出...")
    exit(1)

date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
commit_msg = f"feat: auto publish {date_str}"

res = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
output = res.stdout.decode('utf-8', errors='replace')
if "nothing to commit" in output or "无文件要提交" in output:
    print_success("太棒了，所有文件都已经发布过了，没有任何新修改！")
    time.sleep(2)
    exit(0)

print_step(f"创建提交记录: [{commit_msg}]")

print_step("正在将文章推送到 GitHub 远程仓库...")
res = subprocess.run(["git", "push"], capture_output=True)
if res.returncode != 0:
    print_error("Git push 失败，请检查网络连接！")
    print(res.stderr.decode('utf-8', errors='replace'))
    input("\n按回车键退出...")
    exit(1)

print_success("代码推送完成！")

# Github Actions status checking
import webbrowser

REPO = "Xynrin/Xynrin.github.io"
print_step("正在通过浏览器打开 GitHub Actions 面板...")
try:
    webbrowser.open(f"https://github.com/{REPO}/actions")
    print_success("已自动为你打开浏览器！你可以在网页上直观地查看部署进度。")
except Exception:
    print_step(f"自动打开失败，请手动访问: https://github.com/{REPO}/actions")

print("\n")
input("按回车键退出本窗口...")

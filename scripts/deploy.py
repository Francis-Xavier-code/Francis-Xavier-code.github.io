import os
import subprocess
import datetime
import time

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


def run_cmd(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print(res.stderr)
    return res


def is_nothing_to_commit(res):
    text = f"{res.stdout}\n{res.stderr}"
    return "nothing to commit" in text or "无文件要提交" in text or "没有要提交" in text


print_header("🚀 Black Cat's Blog - 一键发布部署 🚀")

print_step("正在分析本地文件变更...")
res = run_cmd(["git", "add", "."])
if res.returncode != 0:
    print_error("Git add 失败！")
    input("\n按回车键退出...")
    exit(1)

date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
commit_msg = f"feat: auto publish {date_str}"

print_step(f"创建提交记录: [{commit_msg}]")
res = run_cmd(["git", "commit", "-m", commit_msg])
if res.returncode != 0:
    if is_nothing_to_commit(res):
        print_success("没有新的本地修改需要提交，继续检查远程推送...")
    else:
        print_error("Git commit 失败！")
        input("\n按回车键退出...")
        exit(1)

print_step("正在将文章推送到 GitHub 远程仓库...")
res = run_cmd(["git", "push"])
if res.returncode != 0:
    print_error("Git push 失败，请检查网络连接或远程仓库权限！")
    input("\n按回车键退出...")
    exit(1)

print_success("代码推送完成！")

# GitHub Actions status checking
import webbrowser

REPO = "Francis-Xavier-code/Francis-Xavier-code.github.io"
print_step("正在通过浏览器打开 GitHub Actions 面板...")
try:
    webbrowser.open(f"https://github.com/{REPO}/actions")
    print_success("已自动为你打开浏览器！你可以在网页上直观地查看部署进度。")
except Exception:
    print_step(f"自动打开失败，请手动访问: https://github.com/{REPO}/actions")

print("\n")
time.sleep(1)
input("按回车键退出本窗口...")
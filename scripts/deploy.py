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
print_step("正在连接 GitHub Actions 监听部署状态...")

REPO = "Xynrin/Xynrin.github.io"
API_URL = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=1"

# Wait a few seconds for GitHub to register the push and trigger the action
time.sleep(5)

max_retries = 30 # 30 * 5 = 150 seconds timeout
for i in range(max_retries):
    try:
        req = urllib.request.Request(API_URL)
        # Adding a User-Agent is required by GitHub API
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if not data.get('workflow_runs'):
                continue
            
            latest_run = data['workflow_runs'][0]
            status = latest_run['status']
            conclusion = latest_run['conclusion']
            
            # Simple spinner
            spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'][i % 10]
            
            if status in ['queued', 'in_progress']:
                sys.stdout.write(f"\r{C_YELLOW}{spinner} 远程服务器正在编译打包网站中 (状态: {status})...{C_RESET}")
                sys.stdout.flush()
            elif status == 'completed':
                print("\n")
                if conclusion == 'success':
                    print_success("🎉 远程部署大成功！你的网站已经更新至最新版本！")
                    print_step("可以直接在浏览器访问: https://xynrin.github.io")
                else:
                    print_error(f"⚠️ 远程部署失败了 (原因: {conclusion})，请登录 GitHub Actions 查看详情！")
                break
    except Exception as e:
        sys.stdout.write(f"\r{C_YELLOW}⚠ 正在尝试获取 GitHub 状态...{C_RESET}")
        sys.stdout.flush()
        
    time.sleep(5)
else:
    print("\n")
    print_error("等待 GitHub 返回状态超时，但你的代码已经推送成功。请稍后自行访问博客检查。")

print("\n")
input("按回车键退出...")

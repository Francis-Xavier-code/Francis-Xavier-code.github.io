import os
import subprocess
import datetime

# Configure ANSI colors for Windows CMD
os.system("color")

def print_info(msg):
    print(f"[\033[94mINFO\033[0m] {msg}")

def print_success(msg):
    print(f"[\033[92mSUCCESS\033[0m] {msg}")

def print_error(msg):
    print(f"[\033[91mERROR\033[0m] {msg}")

print_info("欢迎使用 Xynrin's Blog 一键发布助手")
print_info("========================================")

print_info("正在将本地更改添加到 Git...")
res = subprocess.run(["git", "add", "."], capture_output=True)
if res.returncode != 0:
    print_error("Git add 失败！")
    print(res.stderr.decode('utf-8', errors='replace'))
    input("按回车键退出...")
    exit(1)

date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
commit_msg = f"feat: auto publish {date_str}"

print_info("正在生成提交记录...")
res = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
output = res.stdout.decode('utf-8', errors='replace')
if "nothing to commit" in output or "无文件要提交" in output:
    print_info("检测到没有文件修改，无需发布。")
    input("按回车键退出...")
    exit(0)

print_info("正在推送到 GitHub，请稍候...")
res = subprocess.run(["git", "push"], capture_output=True)
if res.returncode != 0:
    print_error("Git push 失败，请检查网络连接！")
    print(res.stderr.decode('utf-8', errors='replace'))
    input("按回车键退出...")
    exit(1)

print_success("推送成功！GitHub 正在后台构建你的网站，1-2 分钟后即可生效。")
input("按回车键退出...")

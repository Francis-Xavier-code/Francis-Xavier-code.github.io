import os
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

def prompt_input(msg):
    return input(f"{C_YELLOW}➤{C_RESET} {msg}").strip()

print_header("📝 Xynrin's Blog - 修改文章 📝")

post_dir = os.path.join("content", "post")
if not os.path.exists(post_dir):
    print_error("未找到任何文章！")
    input("\n按回车键退出本窗口...")
    exit(1)

posts = [d for d in os.listdir(post_dir) if os.path.isdir(os.path.join(post_dir, d))]
if not posts:
    print_error("当前还没有发布过任何文章。")
    input("\n按回车键退出本窗口...")
    exit(1)

print_step("找到以下文章：")
for idx, post in enumerate(posts):
    print(f"  {C_BOLD}[{idx + 1}]{C_RESET} {post}")

print("\n")
choice = prompt_input("请输入要修改的文章序号 (输入 0 取消): ")

if not choice.isdigit():
    print_error("请输入有效的数字序号！")
    input("\n按回车键退出本窗口...")
    exit(1)

choice_idx = int(choice)
if choice_idx == 0:
    print_step("操作已取消。")
    exit(0)

if choice_idx < 1 or choice_idx > len(posts):
    print_error("序号超出范围！")
    input("\n按回车键退出本窗口...")
    exit(1)

target_folder = posts[choice_idx - 1]
target_file = os.path.join(post_dir, target_folder, "index.md")

if not os.path.exists(target_file):
    print_error(f"文章主文件不存在: {target_file}")
    input("\n按回车键退出本窗口...")
    exit(1)

print_step(f"正在唤起 Typora 打开 [{target_folder}]...")

try:
    import subprocess
    typora_path = r"C:\Program Files\Typora\Typora.exe"
    if os.path.exists(typora_path):
        p = subprocess.Popen([typora_path, target_file], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.wait()
    else:
        os.startfile(target_file)
except Exception:
    os.startfile(target_file)

print_step("Typora 编辑器已关闭。")
deploy = prompt_input("修改完成了！是否立即一键发布同步到线上？(y/n): ")
if deploy.lower() == 'y':
    os.system("python scripts/deploy.py")
else:
    print_success("好的，修改已保存在本地。")
    print("\n")
    input("按回车键退出本窗口...")

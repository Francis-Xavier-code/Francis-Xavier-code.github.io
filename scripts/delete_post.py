import os
import shutil

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

print_header("🗑️ Black Cat's Blog - 删除文章 🗑️")

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
choice = prompt_input("请输入要删除的文章序号 (输入 0 取消): ")

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
target_dir_path = os.path.join(post_dir, target_folder)

confirm = prompt_input(f"【高危警告】确定要永久删除文章 [{target_folder}] 及其所有相关图片吗？(y/n): ")
if confirm.lower() == 'y':
    try:
        shutil.rmtree(target_dir_path)
        print_success(f"文章 [{target_folder}] 已被彻底删除！")
    except Exception as e:
        print_error(f"删除失败: {e}")
else:
    print_step("操作已取消。")

print("\n")
input("按回车键退出本窗口...")

import os
import datetime
import subprocess
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

def prompt_input(msg):
    return input(f"{C_YELLOW}➤{C_RESET} {msg}").strip()

print_header("✨ Xynrin's Blog - 新建文章 ✨")

folder_name = prompt_input("1. 请输入文章缩写 (英文/拼音, 将作为文件夹名和网址): ")
if not folder_name:
    print_error("名称不能为空！")
    input("\n按回车键退出...")
    exit(1)

title = prompt_input("2. 请输入文章标题 (网页上显示的中文标题): ")
if not title:
    print_error("标题不能为空！")
    input("\n按回车键退出...")
    exit(1)

tags_input = prompt_input("3. 请输入标签 (多个用逗号分隔, 直接回车留空): ")
tags = [t.strip() for t in tags_input.split(',')] if tags_input else []

target_dir = os.path.join("content", "post", folder_name)
target_file = os.path.join(target_dir, "index.md")

if os.path.exists(target_dir):
    print_error(f"文件夹 [{folder_name}] 已存在，请换一个名称！")
    input("\n按回车键退出...")
    exit(1)

print_step("正在生成文件结构...")
os.makedirs(target_dir)

date_str = datetime.datetime.now().strftime("%Y-%m-%d")

with open(target_file, "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write(f'title: "{title}"\n')
    f.write(f'date: {date_str}\n')
    f.write(f'slug: "{folder_name}"\n')
    f.write('description: ""\n')
    f.write('categories:\n')
    f.write('  - 随笔\n')
    if tags:
        f.write('tags:\n')
        for tag in tags:
            if tag:
                f.write(f'  - {tag}\n')
    f.write('draft: false\n')
    f.write('---\n\n')
    f.write('在这里开始写你的正文...\n')

print_success(f"文章已创建: {target_file}")
print_step("正在唤起 Typora 编辑器...")

# 尝试在 PATH 中直接唤醒 typora
res = subprocess.run(["typora", target_file], shell=True, capture_output=True)
if res.returncode != 0:
    # 尝试常见的系统安装路径
    typora_path = r"C:\Program Files\Typora\Typora.exe"
    if os.path.exists(typora_path):
        subprocess.run([typora_path, target_file])
    else:
        print_step("未在系统路径中找到 Typora，将使用系统默认 Markdown 软件打开...")
        os.startfile(target_file)

print_success("一切就绪！祝写作愉快~")
time.sleep(2)

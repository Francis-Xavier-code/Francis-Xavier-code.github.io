import os
import datetime
import subprocess

# Configure ANSI colors for Windows CMD
os.system("color")

def print_info(msg):
    print(f"[\033[94mINFO\033[0m] {msg}")

def print_success(msg):
    print(f"[\033[92mSUCCESS\033[0m] {msg}")

def print_error(msg):
    print(f"[\033[91mERROR\033[0m] {msg}")

def print_prompt(msg):
    return input(f"[\033[93mPROMPT\033[0m] {msg}")

print_info("欢迎使用 Xynrin's Blog 写作助手")
print_info("====================================")

folder_name = print_prompt("请输入文章的英文或拼音缩写（用于文件夹名和网址）: ").strip()
if not folder_name:
    print_error("名称不能为空！")
    input("按回车键退出...")
    exit(1)

title = print_prompt("请输入文章标题（显示在网页上的中文标题）: ").strip()
if not title:
    print_error("标题不能为空！")
    input("按回车键退出...")
    exit(1)

tags_input = print_prompt("请输入文章标签 (多个标签用逗号分隔，直接回车则留空): ").strip()
tags = [t.strip() for t in tags_input.split(',')] if tags_input else []

target_dir = os.path.join("content", "post", folder_name)
target_file = os.path.join(target_dir, "index.md")

if os.path.exists(target_dir):
    print_error(f"文件夹 {folder_name} 已存在，请换一个名称！")
    input("按回车键退出...")
    exit(1)

os.makedirs(target_dir)

date_str = datetime.datetime.now().strftime("%Y-%m-%d")

with open(target_file, "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write(f'title: "{title}"\n')
    f.write(f'date: {date_str}\n')
    f.write(f'slug: "{folder_name}"\n')
    f.write('description: ""\n')
    f.write('categories:\n')
    f.write('  - 默认分类\n')
    if tags:
        f.write('tags:\n')
        for tag in tags:
            if tag:
                f.write(f'  - {tag}\n')
    f.write('draft: false\n')
    f.write('---\n\n')
    f.write('在这里开始写你的正文...\n')

print_success(f"文章已成功创建: {target_file}")
print_info("正在尝试使用 Typora 打开文件...")

try:
    # Attempt to open with typora
    subprocess.run(["typora", target_file], shell=True)
except Exception:
    print_error("找不到 Typora，请确保 Typora 已经添加到系统环境变量。")
    print_info("将尝试使用系统默认程序打开...")
    os.startfile(target_file)

print_success("运行完毕！祝你写作愉快。")

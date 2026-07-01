"""文章（content/post）相关业务逻辑。"""
import os
import re
import shutil
import datetime
import subprocess

from config import POSTS_DIR
from markdown_utils import parse_md, write_md


def _to_list(value):
    """把前端传来的标签/分类规整为去重后的字符串列表。

    支持数组，或用逗号 / 中文逗号 / 空格分隔的字符串。
    """
    if value is None:
        return []
    if isinstance(value, str):
        parts = re.split(r"[,，\s]+", value)
    elif isinstance(value, list):
        parts = [str(v) for v in value]
    else:
        return []
    result = []
    for p in parts:
        p = p.strip()
        if p and p not in result:
            result.append(p)
    return result


def get_all_posts_list():
    """返回按日期倒序排列的文章列表。"""
    posts_list = []
    if not os.path.exists(POSTS_DIR):
        return []
    for folder in os.listdir(POSTS_DIR):
        folder_path = os.path.join(POSTS_DIR, folder)
        if os.path.isdir(folder_path):
            file_path = os.path.join(folder_path, "index.md")
            if os.path.exists(file_path):
                try:
                    fm, _ = parse_md(file_path)
                    posts_list.append({
                        "slug": folder,
                        "title": fm.get("title", folder),
                        "date": fm.get("date", ""),
                        "draft": fm.get("draft", False),
                        "description": fm.get("description", ""),
                    })
                except Exception as e:
                    print(f"Error parsing post {folder}: {e}")
    posts_list.sort(key=lambda x: x.get("date", ""), reverse=True)
    return posts_list


def create_post(data):
    title = (data.get("title") or "").strip()
    slug = (data.get("slug") or "").strip()
    description = (data.get("description") or "").strip()
    categories = _to_list(data.get("categories"))
    tags = _to_list(data.get("tags"))

    if not title or not slug:
        return {"status": "error", "message": "标题和 Slug 不能为空"}, 400

    slug = re.sub(r"[^a-zA-Z0-9\-]", "", slug.replace(" ", "-")).lower()
    if not slug:
        return {"status": "error", "message": "Slug 不合法，请使用字母数字"}, 400

    folder_path = os.path.join(POSTS_DIR, slug)
    if os.path.exists(folder_path):
        return {"status": "error", "message": "该 Slug 已存在，请换一个"}, 400

    file_path = os.path.join(folder_path, "index.md")
    fm = {
        "title": title,
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "draft": True,
        "description": description,
        "categories": categories,
        "tags": tags,
    }
    body = "<!-- 在这里开始编写您的文章内容 -->\n"
    write_md(file_path, fm, body)
    return {"status": "success", "slug": slug}, 200


def delete_post(slug):
    folder_path = os.path.join(POSTS_DIR, slug)
    # 防止路径穿越
    if os.path.commonpath([os.path.abspath(folder_path), POSTS_DIR]) != POSTS_DIR:
        return {"status": "error", "message": "非法路径"}, 400
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        return {"status": "success"}, 200
    return {"status": "error", "message": "文章不存在"}, 404


def edit_post(slug):
    file_path = os.path.join(POSTS_DIR, slug, "index.md")
    if os.path.exists(file_path):
        typora_path = r"C:\Program Files\Typora\Typora.exe"
        if os.path.exists(typora_path):
            subprocess.Popen([typora_path, file_path])
        else:
            os.startfile(file_path)
        return {"status": "success"}, 200
    return {"status": "error", "message": "文件不存在"}, 404

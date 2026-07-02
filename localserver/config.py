"""路径与全局常量配置。"""
import os

# localserver/ 的父目录即仓库根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POSTS_DIR = os.path.join(ROOT_DIR, "content", "post")
MEMOS_DIR = os.path.join(ROOT_DIR, "content", "memos")
STATIC_MEMOS_IMG_DIR = os.path.join(ROOT_DIR, "static", "img", "memos")
STATIC_PHOTOS_IMG_DIR = os.path.join(ROOT_DIR, "static", "img", "photos")
PHOTOS_DATA_FILE = os.path.join(ROOT_DIR, "data", "photos.json")

# 前端静态资源目录（本管理后台自身的页面）
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

HOST = "127.0.0.1"
PORT = 5000

# 允许上传的媒体扩展名
ALLOWED_IMG_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_VIDEO_EXT = {".mp4", ".webm", ".mov", ".m4v"}
ALLOWED_MEDIA_EXT = ALLOWED_IMG_EXT | ALLOWED_VIDEO_EXT


def ensure_dirs():
    """确保运行所需目录都存在。"""
    os.makedirs(STATIC_MEMOS_IMG_DIR, exist_ok=True)
    os.makedirs(STATIC_PHOTOS_IMG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(PHOTOS_DATA_FILE), exist_ok=True)
    os.makedirs(MEMOS_DIR, exist_ok=True)
    os.makedirs(POSTS_DIR, exist_ok=True)
    if not os.path.exists(PHOTOS_DATA_FILE):
        with open(PHOTOS_DATA_FILE, "w", encoding="utf-8", newline="\n") as f:
            f.write("[]\n")

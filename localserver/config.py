"""路径与全局常量配置。"""
import os

# localserver/ 的父目录即仓库根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POSTS_DIR = os.path.join(ROOT_DIR, "content", "post")

# 前端静态资源目录（本管理后台自身的页面）
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

HOST = "127.0.0.1"
PORT = 5000

def ensure_dirs():
    """确保文章目录存在。"""
    os.makedirs(POSTS_DIR, exist_ok=True)

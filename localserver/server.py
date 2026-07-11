"""Xynrin 博客本地管理后台 —— HTTP 服务入口。

职责仅限于：路由分发、静态文件服务、请求/响应封装。
具体业务逻辑分别在 posts / deploy 模块中。
"""
import os
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote

import config
import posts
import deploy

# 静态文件扩展名 -> MIME
MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mov": "video/quicktime",
    ".m4v": "video/x-m4v",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}


class AdminHTTPHandler(BaseHTTPRequestHandler):
    # ---------- 响应辅助 ----------
    def log_message(self, fmt, *args):
        print(f"[{self.date_time_string()}] {fmt % args}")

    def _set_common_headers(self):
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", f"http://{config.HOST}:{config.PORT}")

    def is_same_origin_request(self):
        allowed = {
            f"http://{config.HOST}:{config.PORT}",
            f"http://localhost:{config.PORT}",
        }
        origin = self.headers.get("Origin")
        if origin:
            return origin in allowed
        referer = self.headers.get("Referer")
        if referer:
            parsed = urlparse(referer)
            return f"{parsed.scheme}://{parsed.netloc}" in allowed
        return True

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._set_common_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_bytes(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self._set_common_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_status(self, status):
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self._set_common_headers()
        self.end_headers()

    # ---------- 静态文件 ----------
    def serve_static(self, rel_path):
        """从 localserver/static 安全地提供静态资源。"""
        if rel_path in ("", "/"):
            rel_path = "index.html"
        rel_path = rel_path.lstrip("/")
        full_path = os.path.normpath(os.path.join(config.WEB_DIR, rel_path))
        # 防止路径穿越
        if os.path.commonpath([full_path, config.WEB_DIR]) != config.WEB_DIR:
            self.send_status(403)
            return
        if not os.path.isfile(full_path):
            self.send_status(404)
            return
        ext = os.path.splitext(full_path)[1].lower()
        mime = MIME_TYPES.get(ext, "application/octet-stream")
        with open(full_path, "rb") as f:
            self.send_bytes(f.read(), mime)

    # ---------- 路由 ----------
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self._set_common_headers()
        self.end_headers()

    def do_GET(self):
        path = unquote(urlparse(self.path).path)

        if path == "/api/posts":
            self.send_json(posts.get_all_posts_list())
        else:
            # 其余一律当作静态资源（含首页 index.html）
            self.serve_static(path)

    def do_POST(self):
        if not self.is_same_origin_request():
            self.send_json({"status": "error", "message": "拒绝跨站请求"}, 403)
            return
        path = unquote(urlparse(self.path).path)

        if path == "/api/posts":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            self.send_json(*posts.create_post(data))
        elif path.startswith("/api/posts/edit/"):
            slug = path.rsplit("/", 1)[-1]
            self.send_json(*posts.edit_post(slug))
        elif path == "/api/deploy":
            self.send_json(*deploy.run_deploy())
        else:
            self.send_status(404)

    def do_DELETE(self):
        if not self.is_same_origin_request():
            self.send_json({"status": "error", "message": "拒绝跨站请求"}, 403)
            return
        path = unquote(urlparse(self.path).path)

        if path.startswith("/api/posts/"):
            slug = path.rsplit("/", 1)[-1]
            self.send_json(*posts.delete_post(slug))
        else:
            self.send_status(404)


def run_server():
    config.ensure_dirs()
    address = (config.HOST, config.PORT)
    httpd = ThreadingHTTPServer(address, AdminHTTPHandler)
    url = f"http://{config.HOST}:{config.PORT}"
    print(f"Xynrin Blog Admin is running at {url}")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()

import os
import sys
import json
import datetime
import subprocess
import webbrowser
import shutil
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from email.parser import BytesParser
from email.policy import default

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT_DIR, "content", "post")
MEMOS_DIR = os.path.join(ROOT_DIR, "content", "memos")
STATIC_MEMOS_IMG_DIR = os.path.join(ROOT_DIR, "static", "img", "memos")

os.makedirs(STATIC_MEMOS_IMG_DIR, exist_ok=True)
os.makedirs(MEMOS_DIR, exist_ok=True)
os.makedirs(POSTS_DIR, exist_ok=True)

# Helper: Parse Hugo Markdown Front Matter
def parse_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    parts = content.split('---', 2)
    fm = {}
    body = content
    if len(parts) >= 3:
        front_matter_str = parts[1]
        body = parts[2].strip()
        # Parse simple YAML-like lines
        for line in front_matter_str.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip()
                # Handle boolean
                if val.lower() == 'true':
                    val = True
                elif val.lower() == 'false':
                    val = False
                # Handle string quotes
                elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                # Handle simple list
                elif val.startswith('[') and val.endswith(']'):
                    val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(',') if v.strip()]
                # Handle list in block style
                elif val == '':
                    pass
                fm[key] = val
    return fm, body

# Helper: Write Hugo Markdown Front Matter
def write_md(filepath, fm, body):
    fm_lines = ['---']
    for k, v in fm.items():
        if isinstance(v, bool):
            fm_lines.append(f"{k}: {str(v).lower()}")
        elif isinstance(v, list):
            if len(v) == 0:
                fm_lines.append(f"{k}: []")
            else:
                fm_lines.append(f"{k}:")
                for item in v:
                    fm_lines.append(f"  - {item}")
        else:
            fm_lines.append(f'{k}: "{v}"')
    fm_lines.append('---')
    fm_lines.append('')
    fm_lines.append(body)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(fm_lines))

def get_all_posts_list():
    posts_list = []
    if not os.path.exists(POSTS_DIR):
        return []
    for folder in os.listdir(POSTS_DIR):
        folder_path = os.path.join(POSTS_DIR, folder)
        if os.path.isdir(folder_path):
            file_path = os.path.join(folder_path, "index.md")
            if os.path.exists(file_path):
                try:
                    fm, body = parse_md(file_path)
                    posts_list.append({
                        "slug": folder,
                        "title": fm.get("title", folder),
                        "date": fm.get("date", ""),
                        "draft": fm.get("draft", False),
                        "description": fm.get("description", "")
                    })
                except Exception as e:
                    print(f"Error parsing post {folder}: {e}")
    posts_list.sort(key=lambda x: x.get('date', ''), reverse=True)
    return posts_list

def handle_create_post(data):
    title = data.get('title', '').strip()
    slug = data.get('slug', '').strip()
    description = data.get('description', '').strip()
    
    if not title or not slug:
        return {"status": "error", "message": "标题和 Slug 不能为空"}, 400
    
    slug = re.sub(r'[^a-zA-Z0-9\-]', '', slug.replace(' ', '-')).lower()
    folder_path = os.path.join(POSTS_DIR, slug)
    if os.path.exists(folder_path):
        return {"status": "error", "message": "该 Slug 已存在，请换一个"}, 400
        
    file_path = os.path.join(folder_path, "index.md")
    fm = {
        "title": title,
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "draft": True,
        "description": description
    }
    body = "<!-- 在这里开始编写您的文章内容 -->\n"
    write_md(file_path, fm, body)
    return {"status": "success", "slug": slug}, 200

def handle_delete_post(slug):
    folder_path = os.path.join(POSTS_DIR, slug)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        return {"status": "success"}, 200
    return {"status": "error", "message": "文章不存在"}, 404

def handle_edit_post(slug):
    file_path = os.path.join(POSTS_DIR, slug, "index.md")
    if os.path.exists(file_path):
        typora_path = r"C:\Program Files\Typora\Typora.exe"
        if os.path.exists(typora_path):
            subprocess.Popen([typora_path, file_path])
        else:
            os.startfile(file_path)
        return {"status": "success"}, 200
    return {"status": "error", "message": "文件不存在"}, 404

def get_all_memos_list():
    memos_list = []
    if not os.path.exists(MEMOS_DIR):
        return []
    for file in os.listdir(MEMOS_DIR):
        if file.endswith('.md') and file != '_index.md':
            file_path = os.path.join(MEMOS_DIR, file)
            try:
                fm, body = parse_md(file_path)
                memos_list.append({
                    "id": file,
                    "date": fm.get("date", ""),
                    "images": fm.get("images", []),
                    "content": body
                })
            except Exception as e:
                print(f"Error parsing memo {file}: {e}")
    memos_list.sort(key=lambda x: x.get('date', ''), reverse=True)
    return memos_list

def handle_delete_memo(filename):
    file_path = os.path.join(MEMOS_DIR, filename)
    if os.path.exists(file_path):
        try:
            fm, body = parse_md(file_path)
            for img in fm.get("images", []):
                if img.startswith("/img/memos/"):
                    img_filename = img.split("/")[-1]
                    img_path = os.path.join(STATIC_MEMOS_IMG_DIR, img_filename)
                    if os.path.exists(img_path):
                        os.remove(img_path)
        except Exception as e:
            print(f"Error cleaning image: {e}")
            
        os.remove(file_path)
        return {"status": "success"}, 200
    return {"status": "error", "message": "瞬间不存在"}, 404

def handle_deploy():
    try:
        cmds = [
            ["git", "add", "."],
            ["git", "commit", "-m", f"feat: auto publish {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
            ["git", "push"]
        ]
        outputs = []
        for cmd in cmds:
            res = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT_DIR)
            outputs.append(f"$ {' '.join(cmd)}\n{res.stdout}\n{res.stderr}")
            if cmd[0] == "git" and cmd[1] == "commit" and res.returncode != 0:
                if "nothing to commit" in res.stdout or "无文件要提交" in res.stdout or "nothing to commit" in res.stderr:
                    outputs.append("（无文件变更需要提交，继续推送...）")
                    continue
        return {"status": "success", "log": "\n".join(outputs)}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def handle_create_memo(content_type, content_length, rfile):
    if not content_type or not content_type.startswith('multipart/form-data'):
        return {"status": "error", "message": "Content-Type must be multipart/form-data"}, 400
        
    data_bytes = rfile.read(content_length)
    headers_raw = f"Content-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n".encode('ascii')
    
    msg = BytesParser(policy=default).parsebytes(headers_raw + data_bytes)
    
    form_fields = {}
    files = []
    
    for part in msg.walk():
        if part.is_multipart():
            continue
        disposition = part.get('Content-Disposition')
        if disposition:
            name_match = re.search(r'name="([^"]+)"', disposition)
            filename_match = re.search(r'filename="([^"]+)"', disposition)
            if name_match:
                name = name_match.group(1)
                payload = part.get_payload(decode=True)
                if filename_match:
                    filename = filename_match.group(1)
                    if filename:
                        files.append((name, filename, payload))
                else:
                    form_fields[name] = payload.decode('utf-8')
                    
    content = form_fields.get('content', '').strip()
    if not content:
        return {"status": "error", "message": "瞬间内容不能为空"}, 400
        
    timestamp_slug = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{datetime.datetime.now().strftime('%Y-%m-%d')}-{timestamp_slug}.md"
    file_path = os.path.join(MEMOS_DIR, filename)
    
    images = []
    for idx, (field_name, original_filename, payload) in enumerate(files):
        ext = os.path.splitext(original_filename)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            img_name = f"memo-{timestamp_slug}-{idx+1}{ext}"
            target_path = os.path.join(STATIC_MEMOS_IMG_DIR, img_name)
            with open(target_path, 'wb') as f:
                f.write(payload)
            images.append(f"/img/memos/{img_name}")
            
    fm = {
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    }
    if images:
        fm["images"] = images
        
    write_md(file_path, fm, content)
    return {"status": "success"}, 200

class AdminHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Print logs to console
        print(f"[{self.date_time_string()}] {format%args}")

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def send_html(self, html, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/':
            self.send_html(get_index_html())
        elif path == '/api/posts':
            self.send_json(get_all_posts_list())
        elif path == '/api/memos':
            self.send_json(get_all_memos_list())
        elif path.startswith('/img/memos/'):
            img_filename = path.split('/')[-1]
            img_path = os.path.join(STATIC_MEMOS_IMG_DIR, img_filename)
            if os.path.exists(img_path):
                self.send_response(200)
                ext = os.path.splitext(img_path)[1].lower()
                mime = 'image/png'
                if ext in ['.jpg', '.jpeg']: mime = 'image/jpeg'
                elif ext == '.gif': mime = 'image/gif'
                elif ext == '.webp': mime = 'image/webp'
                self.send_header('Content-Type', mime)
                self.end_headers()
                with open(img_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/api/posts':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            res, status = handle_create_post(data)
            self.send_json(res, status)
            
        elif path.startswith('/api/posts/edit/'):
            slug = path.split('/')[-1]
            res, status = handle_edit_post(slug)
            self.send_json(res, status)
            
        elif path == '/api/memos':
            content_type = self.headers.get('Content-Type')
            content_length = int(self.headers.get('Content-Length', 0))
            res, status = handle_create_memo(content_type, content_length, self.rfile)
            self.send_json(res, status)
            
        elif path == '/api/deploy':
            res, status = handle_deploy()
            self.send_json(res, status)
            
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path.startswith('/api/posts/'):
            slug = path.split('/')[-1]
            res, status = handle_delete_post(slug)
            self.send_json(res, status)
            
        elif path.startswith('/api/memos/'):
            filename = path.split('/')[-1]
            res, status = handle_delete_memo(filename)
            self.send_json(res, status)
            
        else:
            self.send_response(404)
            self.end_headers()

def get_index_html():
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xynrin's Blog - 本地管理后台</title>
    <style>
        :root {
            --bg-color: #1d1e20;
            --card-bg: #2e2e33;
            --text-color: #f8f9fa;
            --text-muted: #a5a6a7;
            --border-color: #3e3e43;
            --primary-color: #3b82f6;
            --primary-hover: #2563eb;
            --danger-color: #ef4444;
            --success-color: #10b981;
            --radius: 8px;
            --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.5;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* Sidebar */
        .sidebar {
            width: 260px;
            background-color: #151618;
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            padding: 1.5rem;
            flex-shrink: 0;
        }

        .logo-area {
            font-size: 1.25rem;
            font-weight: bold;
            color: var(--text-color);
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 10px;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
        }

        .menu-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
            flex-grow: 1;
        }

        .menu-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border-radius: var(--radius);
            color: var(--text-muted);
            text-decoration: none;
            cursor: pointer;
            transition: var(--transition);
            font-weight: 500;
        }

        .menu-item:hover, .menu-item.active {
            background-color: var(--card-bg);
            color: var(--text-color);
        }

        .menu-item.active {
            border-left: 4px solid var(--primary-color);
            border-top-left-radius: 0;
            border-bottom-left-radius: 0;
        }

        /* Main Content */
        .main-container {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            background: radial-gradient(circle at top right, rgba(59, 130, 246, 0.05), transparent 400px);
        }

        .header {
            height: 60px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 2rem;
            flex-shrink: 0;
        }

        .content-body {
            padding: 2rem;
            overflow-y: auto;
            flex-grow: 1;
        }

        /* Page Container */
        .page {
            display: none;
            animation: fadeIn 0.3s ease;
        }

        .page.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Cards & Lists */
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: var(--radius);
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }

        .btn:hover {
            background-color: var(--primary-hover);
        }

        .btn-danger {
            background-color: var(--danger-color);
        }
        .btn-danger:hover {
            background-color: #dc2626;
        }
        .btn-secondary {
            background-color: #4b5563;
        }
        .btn-secondary:hover {
            background-color: #374151;
        }

        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        /* Lists Table/Cards */
        .item-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .list-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem;
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            transition: var(--transition);
        }

        .list-row:hover {
            border-color: #4e4e53;
            transform: translateY(-2px);
        }

        .item-meta {
            display: flex;
            flex-direction: column;
            gap: 4px;
            min-width: 0;
        }

        .item-title {
            font-weight: bold;
            font-size: 16px;
            color: var(--text-color);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .item-subtitle {
            font-size: 12px;
            color: var(--text-muted);
            display: flex;
            gap: 12px;
        }

        .badge {
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .badge-draft {
            background-color: #f59e0b;
            color: #1e1b4b;
        }
        .badge-pub {
            background-color: var(--success-color);
            color: #064e3b;
        }

        .actions {
            display: flex;
            gap: 8px;
            flex-shrink: 0;
        }

        /* Forms */
        .form-group {
            margin-bottom: 1.25rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 6px;
            font-weight: 500;
            font-size: 14px;
            color: var(--text-muted);
        }

        .form-control {
            width: 100%;
            background-color: #1d1e20;
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 10px 12px;
            color: var(--text-color);
            font-size: 14px;
            outline: none;
            transition: var(--transition);
        }

        .form-control:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }

        textarea.form-control {
            min-height: 120px;
            resize: vertical;
            font-family: inherit;
        }

        /* Dropzone */
        .dropzone {
            border: 2px dashed var(--border-color);
            padding: 2rem;
            text-align: center;
            border-radius: var(--radius);
            cursor: pointer;
            transition: var(--transition);
            background-color: rgba(255, 255, 255, 0.01);
        }

        .dropzone:hover {
            border-color: var(--primary-color);
            background-color: rgba(59, 130, 246, 0.02);
        }

        .preview-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            gap: 10px;
            margin-top: 1rem;
        }

        .preview-img {
            width: 80px;
            height: 80px;
            object-fit: cover;
            border-radius: 4px;
            border: 1px solid var(--border-color);
            position: relative;
        }

        /* Terminal Console */
        .console {
            background-color: #101112;
            font-family: Consolas, Monaco, "Courier New", monospace;
            padding: 1.5rem;
            border-radius: var(--radius);
            min-height: 300px;
            max-height: 500px;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            color: #34d399;
            font-size: 13px;
            white-space: pre-wrap;
        }

        /* Modal styling */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(4px);
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        .modal.active {
            display: flex;
        }
        .modal-content {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            width: 500px;
            max-width: 90%;
            padding: 1.5rem;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        }

        /* Alerts */
        .toast {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background-color: var(--success-color);
            color: white;
            padding: 12px 24px;
            border-radius: var(--radius);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            z-index: 2000;
        }
        .toast.show {
            transform: translateY(0);
            opacity: 1;
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="logo-area">
            <span>🫧 Xynrin Admin</span>
        </div>
        <ul class="menu-list">
            <li class="menu-item active" onclick="switchPage('posts-page', this)">📝 文章管理</li>
            <li class="menu-item" onclick="switchPage('memos-page', this)">🫧 瞬间记录</li>
            <li class="menu-item" onclick="switchPage('deploy-page', this)">🚀 网站发布</li>
        </ul>
        <div style="font-size: 11px; color: var(--text-muted); text-align: center; margin-top: auto;">
            Xynrin.github.io &copy; 2026
        </div>
    </div>

    <!-- Main Container -->
    <div class="main-container">
        <div class="header">
            <h2 id="page-title" style="font-size: 1.125rem;">文章管理</h2>
            <div id="status-indicator" style="display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted);">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: var(--success-color);"></div> 本地服务已连接
            </div>
        </div>

        <div class="content-body">
            <!-- PAGE: Posts -->
            <div id="posts-page" class="page active">
                <div class="panel-header">
                    <h3>全部文章</h3>
                    <button class="btn" onclick="openModal('new-post-modal')">+ 新增文章</button>
                </div>
                <div id="posts-list" class="item-list">
                    <!-- Loaded dynamically -->
                </div>
            </div>

            <!-- PAGE: Memos -->
            <div id="memos-page" class="page">
                <div class="panel-header">
                    <h3>记录瞬间（朋友圈）</h3>
                </div>
                <div class="card" style="margin-bottom: 2rem;">
                    <form id="memo-form">
                        <div class="form-group">
                            <label>瞬间内容</label>
                            <textarea id="memo-content" class="form-control" placeholder="写下你现在的想法..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>上传图片（支持拖拽或点击多选，上限 9 张）</label>
                            <div class="dropzone" onclick="document.getElementById('memo-images-input').click()" id="dropzone">
                                <span style="font-size: 14px; color: var(--text-muted);">拖拽图片到这里，或点击选择图片上传</span>
                                <input type="file" id="memo-images-input" multiple accept="image/*" style="display: none;" onchange="handleFileSelect(event)">
                                <div id="previews" class="preview-container"></div>
                            </div>
                        </div>
                        <button type="button" class="btn" onclick="submitMemo()" id="memo-submit-btn">发布瞬间</button>
                    </form>
                </div>
                
                <h3 style="margin-bottom: 1rem;">瞬间历史流</h3>
                <div id="memos-list" class="item-list">
                    <!-- Loaded dynamically -->
                </div>
            </div>

            <!-- PAGE: Deploy -->
            <div id="deploy-page" class="page">
                <div class="panel-header">
                    <h3>一键发布站点</h3>
                </div>
                <div class="card" style="margin-bottom: 1.5rem;">
                    <p style="margin-bottom: 1.25rem; color: var(--text-muted); font-size: 14px;">
                        点击下方按钮将自动执行 Git 代码打包与推送流程，自动将当前修改部署发布到您的 GitHub Pages 远程网站。
                    </p>
                    <button class="btn" onclick="runDeploy()" id="deploy-btn">🚀 立即推送部署上线</button>
                </div>
                <h4 style="margin-bottom: 0.5rem; font-size: 14px; color: var(--text-muted);">执行日志</h4>
                <div id="console" class="console">准备就绪。等待运行命令...</div>
            </div>
        </div>
    </div>

    <!-- Modal: New Post -->
    <div id="new-post-modal" class="modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 1.25rem;">创建新文章</h3>
            <form id="new-post-form">
                <div class="form-group">
                    <label>文章标题 (Title)</label>
                    <input type="text" id="post-title-input" class="form-control" placeholder="输入文章标题..." required>
                </div>
                <div class="form-group">
                    <label>文件名标识 (Slug，仅限字母数字和横杠，用于文件夹名)</label>
                    <input type="text" id="post-slug-input" class="form-control" placeholder="例如: my-new-post" required>
                </div>
                <div class="form-group">
                    <label>描述信息 (Description)</label>
                    <input type="text" id="post-desc-input" class="form-control" placeholder="简短的一句话描述...">
                </div>
                <div class="actions" style="justify-content: flex-end; margin-top: 1.5rem;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('new-post-modal')">取消</button>
                    <button type="submit" class="btn">确认创建</button>
                </div>
            </form>
        </div>
    </div>

    <div id="toast" class="toast">操作成功！</div>

    <!-- JavaScript logic -->
    <script>
        let selectedFiles = [];

        function switchPage(pageId, menuItem) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
            
            document.getElementById(pageId).classList.add('active');
            menuItem.classList.add('active');
            
            const titleMap = {
                'posts-page': '文章管理',
                'memos-page': '瞬间记录',
                'deploy-page': '网站发布'
            };
            document.getElementById('page-title').innerText = titleMap[pageId];

            if (pageId === 'posts-page') loadPosts();
            if (pageId === 'memos-page') loadMemos();
        }

        function showToast(msg, isError = false) {
            const toast = document.getElementById('toast');
            toast.innerText = msg;
            toast.style.backgroundColor = isError ? 'var(--danger-color)' : 'var(--success-color)';
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }

        function openModal(id) {
            document.getElementById(id).classList.add('active');
        }

        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
            document.getElementById('new-post-form').reset();
        }

        // --- Posts Logics ---
        async function loadPosts() {
            const res = await fetch('/api/posts');
            const posts = await res.json();
            const list = document.getElementById('posts-list');
            list.innerHTML = '';
            
            if (posts.length === 0) {
                list.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 2rem;">当前无任何文章</div>';
                return;
            }

            posts.forEach(post => {
                const dateStr = post.date ? post.date.substring(0, 10) : '无日期';
                const badge = post.draft ? 
                    '<span class="badge badge-draft">草稿</span>' : 
                    '<span class="badge badge-pub">已发布</span>';
                
                list.innerHTML += `
                    <div class="list-row">
                        <div class="item-meta">
                            <div class="item-title" title="${post.title}">${post.title}</div>
                            <div class="item-subtitle">
                                <span>📅 ${dateStr}</span>
                                <span>📁 content/post/${post.slug}</span>
                                ${badge}
                            </div>
                        </div>
                        <div class="actions">
                            <button class="btn btn-secondary" onclick="editPost('${post.slug}')">✒️ 编辑</button>
                            <button class="btn btn-danger" onclick="deletePost('${post.slug}')">🗑️ 删除</button>
                        </div>
                    </div>
                `;
            });
        }

        async function editPost(slug) {
            const res = await fetch(`/api/posts/edit/${slug}`, { method: 'POST' });
            const data = await res.json();
            if (data.status === 'success') {
                showToast("已成功唤起 Typora / 系统编辑器打开文章！");
            } else {
                showToast(data.message, true);
            }
        }

        async function deletePost(slug) {
            if (confirm(`确认要彻底删除文章 [${slug}] 吗？此操作无法恢复！`)) {
                const res = await fetch(`/api/posts/${slug}`, { method: 'DELETE' });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast("文章删除成功！");
                    loadPosts();
                } else {
                    showToast(data.message, true);
                }
            }
        }

        document.getElementById('new-post-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('post-title-input').value;
            const slug = document.getElementById('post-slug-input').value;
            const description = document.getElementById('post-desc-input').value;

            const res = await fetch('/api/posts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, slug, description })
            });
            const data = await res.json();

            if (data.status === 'success') {
                showToast("文章创建成功！即将自动唤起编辑器...");
                closeModal('new-post-modal');
                loadPosts();
                setTimeout(() => editPost(data.slug), 1000);
            } else {
                showToast(data.message, true);
            }
        });

        // --- Memos Logics ---
        async function loadMemos() {
            const res = await fetch('/api/memos');
            const memos = await res.json();
            const list = document.getElementById('memos-list');
            list.innerHTML = '';

            if (memos.length === 0) {
                list.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 2rem;">当前无任何瞬间记录</div>';
                return;
            }

            memos.forEach(memo => {
                let imgHtml = '';
                if (memo.images && memo.images.length > 0) {
                    imgHtml = '<div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;">';
                    memo.images.forEach(img => {
                        imgHtml += `<img src="${img}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px; border: 1px solid var(--border-color);">`;
                    });
                    imgHtml += '</div>';
                }

                const dateStr = memo.date ? memo.date.replace('T', ' ').substring(0, 16) : '无时间';
                
                list.innerHTML += `
                    <div class="list-row" style="align-items: flex-start;">
                        <div class="item-meta" style="flex-grow: 1;">
                            <div style="font-size: 14px; white-space: pre-wrap; color: var(--text-color); line-height: 1.6;">${memo.content}</div>
                            ${imgHtml}
                            <div style="font-size: 11px; color: var(--text-muted); margin-top: 8px;">
                                <span>📅 ${dateStr}</span> &middot; <span>文件: ${memo.id}</span>
                            </div>
                        </div>
                        <div class="actions" style="align-self: center;">
                            <button class="btn btn-danger" onclick="deleteMemo('${memo.id}')">🗑️ 删除</button>
                        </div>
                    </div>
                `;
            });
        }

        function handleFileSelect(e) {
            const files = Array.from(e.target.files);
            if (selectedFiles.length + files.length > 9) {
                alert("瞬间最多只能上传 9 张照片！");
                return;
            }
            selectedFiles = selectedFiles.concat(files);
            renderPreviews();
        }

        function renderPreviews() {
            const container = document.getElementById('previews');
            container.innerHTML = '';
            selectedFiles.forEach((file, index) => {
                const reader = new FileReader();
                reader.onload = function(e) {
                    container.innerHTML += `
                        <div style="position: relative; display: inline-block;">
                            <img src="${e.target.result}" class="preview-img">
                            <span onclick="removePreview(${index})" style="position: absolute; top: -5px; right: -5px; background: var(--danger-color); color: white; width: 18px; height: 18px; border-radius: 50%; font-size: 10px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-weight: bold; border: 1px solid var(--bg-color);">✕</span>
                        </div>
                    `;
                }
                reader.readAsDataURL(file);
            });
        }

        function removePreview(index) {
            selectedFiles.splice(index, 1);
            renderPreviews();
        }

        async function submitMemo() {
            const content = document.getElementById('memo-content').value.trim();
            if (!content) {
                showToast("内容不能为空！", true);
                return;
            }

            const btn = document.getElementById('memo-submit-btn');
            btn.disabled = true;
            btn.innerText = "正在发布...";

            const formData = new FormData();
            formData.append('content', content);
            selectedFiles.forEach(file => {
                formData.append('images', file);
            });

            try {
                const res = await fetch('/api/memos', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast("瞬间发布成功！");
                    document.getElementById('memo-content').value = '';
                    selectedFiles = [];
                    renderPreviews();
                    loadMemos();
                } else {
                    showToast(data.message, true);
                }
            } catch (err) {
                showToast("网络错误，发布失败", true);
            } finally {
                btn.disabled = false;
                btn.innerText = "发布瞬间";
            }
        }

        async function deleteMemo(id) {
            if (confirm("确定要删除这条瞬间吗？图片文件也会一同清理。")) {
                const res = await fetch(`/api/memos/${id}`, { method: 'DELETE' });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast("删除瞬间成功！");
                    loadMemos();
                } else {
                    showToast(data.message, true);
                }
            }
        }

        async function runDeploy() {
            const btn = document.getElementById('deploy-btn');
            const consoleDiv = document.getElementById('console');
            
            btn.disabled = true;
            btn.innerText = "正在推送部署中...";
            consoleDiv.innerText = "🚀 开始执行 Git 一键同步推送...\n";

            try {
                const res = await fetch('/api/deploy', { method: 'POST' });
                const data = await res.json();
                if (data.status === 'success') {
                    consoleDiv.innerText += data.log + "\\n\\n✨ 部署推送流程执行完成！请在 GitHub Actions 查看运行情况！";
                    showToast("代码部署推送成功！");
                } else {
                    consoleDiv.innerText += "❌ 失败了: " + data.message;
                    showToast("部署失败！", true);
                }
            } catch(e) {
                consoleDiv.innerText += "❌ 网络连接或服务错误。";
                showToast("网络错误，执行失败", true);
            } finally {
                btn.disabled = false;
                btn.innerText = "🚀 立即推送部署上线";
            }
        }

        loadPosts();
        
        const dropzone = document.getElementById('dropzone');
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.style.borderColor = 'var(--primary-color)';
        });
        dropzone.addEventListener('dragleave', () => {
            dropzone.style.borderColor = 'var(--border-color)';
        });
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.style.borderColor = 'var(--border-color)';
            const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
            if (selectedFiles.length + files.length > 9) {
                alert("瞬间最多只能上传 9 张照片！");
                return;
            }
            selectedFiles = selectedFiles.concat(files);
            renderPreviews();
        });
    </script>
</body>
</html>
"""

def run_server():
    server_address = ('127.0.0.1', 5000)
    httpd = HTTPServer(server_address, AdminHTTPHandler)
    print("Xynrin Blog Admin is running at http://127.0.0.1:5000")
    # Automatically open browser
    webbrowser.open("http://127.0.0.1:5000")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == '__main__':
    run_server()

"""瞬间（content/memos）相关业务逻辑。"""
import os
import re
import datetime
from email.parser import BytesParser
from email.policy import default

from config import MEMOS_DIR, STATIC_MEMOS_IMG_DIR, ALLOWED_IMG_EXT
from markdown_utils import parse_md, write_md


def get_all_memos_list():
    """返回按日期倒序排列的瞬间列表。"""
    memos_list = []
    if not os.path.exists(MEMOS_DIR):
        return []
    for file in os.listdir(MEMOS_DIR):
        if file.endswith(".md") and file != "_index.md":
            file_path = os.path.join(MEMOS_DIR, file)
            try:
                fm, body = parse_md(file_path)
                memos_list.append({
                    "id": file,
                    "date": fm.get("date", ""),
                    "images": fm.get("images", []),
                    "content": body,
                })
            except Exception as e:
                print(f"Error parsing memo {file}: {e}")
    memos_list.sort(key=lambda x: x.get("date", ""), reverse=True)
    return memos_list


def delete_memo(filename):
    # 只允许文件名，禁止路径分隔符
    if "/" in filename or "\\" in filename or ".." in filename:
        return {"status": "error", "message": "非法文件名"}, 400
    file_path = os.path.join(MEMOS_DIR, filename)
    if os.path.exists(file_path):
        try:
            fm, _ = parse_md(file_path)
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


def _parse_multipart(content_type, data_bytes):
    """解析 multipart/form-data，返回 (form_fields, files)。"""
    headers_raw = (
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(data_bytes)}\r\n\r\n"
    ).encode("ascii")
    msg = BytesParser(policy=default).parsebytes(headers_raw + data_bytes)

    form_fields = {}
    files = []
    for part in msg.walk():
        if part.is_multipart():
            continue
        disposition = part.get("Content-Disposition")
        if not disposition:
            continue
        name_match = re.search(r'name="([^"]+)"', disposition)
        filename_match = re.search(r'filename="([^"]+)"', disposition)
        if not name_match:
            continue
        name = name_match.group(1)
        payload = part.get_payload(decode=True)
        if filename_match and filename_match.group(1):
            files.append((name, filename_match.group(1), payload))
        elif payload is not None:
            form_fields[name] = payload.decode("utf-8")
    return form_fields, files


def create_memo(content_type, content_length, rfile):
    if not content_type or not content_type.startswith("multipart/form-data"):
        return {"status": "error", "message": "Content-Type must be multipart/form-data"}, 400

    data_bytes = rfile.read(content_length)
    form_fields, files = _parse_multipart(content_type, data_bytes)

    content = (form_fields.get("content") or "").strip()
    if not content:
        return {"status": "error", "message": "瞬间内容不能为空"}, 400

    timestamp_slug = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{datetime.datetime.now().strftime('%Y-%m-%d')}-{timestamp_slug}.md"
    file_path = os.path.join(MEMOS_DIR, filename)

    images = []
    for idx, (_, original_filename, payload) in enumerate(files):
        ext = os.path.splitext(original_filename)[1].lower()
        if ext in ALLOWED_IMG_EXT and payload:
            img_name = f"memo-{timestamp_slug}-{idx + 1}{ext}"
            target_path = os.path.join(STATIC_MEMOS_IMG_DIR, img_name)
            with open(target_path, "wb") as f:
                f.write(payload)
            images.append(f"/img/memos/{img_name}")

    fm = {"date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")}
    if images:
        fm["images"] = images

    write_md(file_path, fm, content)
    return {"status": "success"}, 200

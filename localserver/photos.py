"""独立图片库（data/photos.json + static/img/photos）业务逻辑。"""
import datetime
import json
import os
import re
import uuid
from email.parser import BytesParser
from email.policy import default

from config import ALLOWED_IMG_EXT, PHOTOS_DATA_FILE, STATIC_PHOTOS_IMG_DIR


def _parse_multipart(content_type, data_bytes):
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


def _load_photos():
    if not os.path.exists(PHOTOS_DATA_FILE):
        return []
    try:
        with open(PHOTOS_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_photos(photos):
    os.makedirs(os.path.dirname(PHOTOS_DATA_FILE), exist_ok=True)
    with open(PHOTOS_DATA_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(photos, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _parse_tags(raw):
    return [tag.strip() for tag in re.split(r"[,，\s]+", raw or "") if tag.strip()]


def _normalize_datetime(raw):
    if not raw:
        return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    raw = raw.strip()
    if raw.endswith("+08:00"):
        return raw
    try:
        dt = datetime.datetime.fromisoformat(raw)
    except ValueError:
        return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")


def _metadata_from_fields(fields):
    return {
        "title": (fields.get("title") or "").strip(),
        "description": (fields.get("description") or "").strip(),
        "date": _normalize_datetime(fields.get("date", "")),
        "location": (fields.get("location") or "").strip(),
        "tags": _parse_tags(fields.get("tags") or ""),
        "visibility": (fields.get("visibility") or "public").strip() or "public",
    }


def _store_photo(original_filename, payload, prefix):
    ext = os.path.splitext(original_filename)[1].lower()
    if ext not in ALLOWED_IMG_EXT or not payload:
        return None
    safe_id = f"{prefix}-{uuid.uuid4().hex[:8]}"
    filename = f"photo-{safe_id}{ext}"
    target_path = os.path.join(STATIC_PHOTOS_IMG_DIR, filename)
    os.makedirs(STATIC_PHOTOS_IMG_DIR, exist_ok=True)
    with open(target_path, "wb") as f:
        f.write(payload)
    return {
        "id": safe_id,
        "src": f"/img/photos/{filename}",
        "filename": filename,
        "originalName": os.path.basename(original_filename),
        "size": len(payload),
    }


def _delete_photo_file(src):
    if not src or not src.startswith("/img/photos/"):
        return
    filename = src.split("/")[-1]
    path = os.path.join(STATIC_PHOTOS_IMG_DIR, filename)
    if os.path.exists(path):
        os.remove(path)


def _find_photo(photos, photo_id):
    for index, photo in enumerate(photos):
        if photo.get("id") == photo_id:
            return index, photo
    return -1, None


def get_all_photos():
    photos = _load_photos()
    photos.sort(key=lambda x: x.get("date", ""), reverse=True)
    return photos


def create_photos(content_type, content_length, rfile):
    if not content_type or not content_type.startswith("multipart/form-data"):
        return {"status": "error", "message": "Content-Type must be multipart/form-data"}, 400

    data_bytes = rfile.read(content_length)
    fields, files = _parse_multipart(content_type, data_bytes)
    valid_files = [(name, original, payload) for name, original, payload in files if payload]
    if not valid_files:
        return {"status": "error", "message": "请至少选择一张图片"}, 400

    now_slug = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    meta = _metadata_from_fields(fields)
    photos = _load_photos()
    created = []

    for idx, (_, original_filename, payload) in enumerate(valid_files):
        stored = _store_photo(original_filename, payload, f"{now_slug}-{idx + 1}")
        if not stored:
            continue
        item = {
            **stored,
            **meta,
            "createdAt": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        }
        if not item["title"]:
            item["title"] = os.path.splitext(item["originalName"])[0]
        photos.append(item)
        created.append(item)

    if not created:
        return {"status": "error", "message": "没有可保存的图片，请检查格式"}, 400

    photos.sort(key=lambda x: x.get("date", ""), reverse=True)
    _save_photos(photos)
    return {"status": "success", "count": len(created), "photos": created}, 200


def update_photo(photo_id, content_type, content_length, rfile):
    if "/" in photo_id or "\\" in photo_id or ".." in photo_id:
        return {"status": "error", "message": "非法图片 ID"}, 400
    if not content_type or not content_type.startswith("multipart/form-data"):
        return {"status": "error", "message": "Content-Type must be multipart/form-data"}, 400

    photos = _load_photos()
    index, photo = _find_photo(photos, photo_id)
    if photo is None:
        return {"status": "error", "message": "图片不存在"}, 404

    data_bytes = rfile.read(content_length)
    fields, files = _parse_multipart(content_type, data_bytes)
    photo.update(_metadata_from_fields(fields))

    replacement = next((item for item in files if item[2]), None)
    if replacement:
        _, original_filename, payload = replacement
        stored = _store_photo(original_filename, payload, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        if stored:
            _delete_photo_file(photo.get("src", ""))
            photo.update(stored)

    if not photo.get("title"):
        photo["title"] = os.path.splitext(photo.get("originalName", "未命名图片"))[0]

    photos[index] = photo
    photos.sort(key=lambda x: x.get("date", ""), reverse=True)
    _save_photos(photos)
    return {"status": "success", "photo": photo}, 200


def delete_photo(photo_id):
    if "/" in photo_id or "\\" in photo_id or ".." in photo_id:
        return {"status": "error", "message": "非法图片 ID"}, 400
    photos = _load_photos()
    index, photo = _find_photo(photos, photo_id)
    if photo is None:
        return {"status": "error", "message": "图片不存在"}, 404
    _delete_photo_file(photo.get("src", ""))
    del photos[index]
    _save_photos(photos)
    return {"status": "success"}, 200

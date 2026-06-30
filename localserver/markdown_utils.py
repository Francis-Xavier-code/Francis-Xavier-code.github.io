"""Hugo Markdown Front Matter 的简易解析与写入。

只支持本项目实际用到的 YAML 子集：字符串、布尔、行内列表 [a, b]、
以及块状列表（key: 换行后跟若干 "  - item"）。
"""
import os


def parse_md(filepath):
    """解析 markdown 文件，返回 (front_matter_dict, body_str)。"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("---", 2)
    fm = {}
    body = content
    if len(parts) >= 3:
        front_matter_str = parts[1]
        body = parts[2].strip()
        lines = front_matter_str.strip().split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            if not line or line.startswith("#"):
                continue
            # 块状列表项会在下方被前一个 key 消费掉，
            # 走到这里的裸 "- item" 属于异常，跳过。
            if line.startswith("- "):
                continue
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                # 块状列表：key: 后换行，跟随若干缩进的 "- item"
                if val == "":
                    items = []
                    while i < len(lines) and lines[i].strip().startswith("- "):
                        item = lines[i].strip()[2:].strip().strip('"').strip("'")
                        items.append(item)
                        i += 1
                    if items:
                        val = items
                elif val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
                elif (val.startswith('"') and val.endswith('"')) or (
                    val.startswith("'") and val.endswith("'")
                ):
                    val = val[1:-1]
                # 行内列表
                elif val.startswith("[") and val.endswith("]"):
                    val = [
                        v.strip().strip('"').strip("'")
                        for v in val[1:-1].split(",")
                        if v.strip()
                    ]
                fm[key] = val
    return fm, body


def write_md(filepath, fm, body):
    """将 front matter 与正文写回 markdown 文件（统一 LF 换行）。"""
    fm_lines = ["---"]
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
    fm_lines.append("---")
    fm_lines.append("")
    fm_lines.append(body)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(fm_lines))

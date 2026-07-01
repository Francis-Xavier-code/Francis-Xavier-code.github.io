"""一键 Git 部署逻辑。"""
import datetime
import subprocess

from config import ROOT_DIR


def _run_git(cmd):
    res = subprocess.run(
        cmd, capture_output=True, text=True, cwd=ROOT_DIR,
        encoding="utf-8", errors="replace",
    )
    output = f"$ {' '.join(cmd)}\n{res.stdout}\n{res.stderr}".rstrip()
    return res, output


def _is_nothing_to_commit(res):
    text = f"{res.stdout}\n{res.stderr}"
    return (
        "nothing to commit" in text
        or "无文件要提交" in text
        or "没有要提交" in text
    )


def run_deploy():
    try:
        commit_msg = f"feat: auto publish {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        cmds = [
            ["git", "add", "."],
            ["git", "commit", "-m", commit_msg],
            ["git", "push"],
        ]
        outputs = []
        for cmd in cmds:
            res, output = _run_git(cmd)
            outputs.append(output)
            if res.returncode == 0:
                continue
            if cmd[:2] == ["git", "commit"] and _is_nothing_to_commit(res):
                outputs.append("（无文件变更需要提交，继续推送...）")
                continue
            return {
                "status": "error",
                "message": f"命令执行失败: {' '.join(cmd)}",
                "log": "\n\n".join(outputs),
            }, 500
        return {"status": "success", "log": "\n\n".join(outputs)}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
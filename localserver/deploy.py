"""一键 Git 部署逻辑。"""
import datetime
import subprocess

from config import ROOT_DIR


def run_deploy():
    try:
        cmds = [
            ["git", "add", "."],
            ["git", "commit", "-m",
             f"feat: auto publish {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
            ["git", "push"],
        ]
        outputs = []
        for cmd in cmds:
            res = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT_DIR)
            outputs.append(f"$ {' '.join(cmd)}\n{res.stdout}\n{res.stderr}")
            if cmd[:2] == ["git", "commit"] and res.returncode != 0:
                if ("nothing to commit" in res.stdout
                        or "无文件要提交" in res.stdout
                        or "nothing to commit" in res.stderr):
                    outputs.append("（无文件变更需要提交，继续推送...）")
                    continue
        return {"status": "success", "log": "\n".join(outputs)}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

# -*- coding: utf-8 -*-
"""eNSP 部署知识库小工具：录入问题 / 列出 / 导出离线包 / 同步。

用法：
    python tools/kb.py new "标题"        # 新建一条问题
    python tools/kb.py list [关键字]      # 列出问题
    python tools/kb.py show 0003          # 查看某条
    python tools/kb.py export             # 导出离线 zip 到 kb_local/exports
    python tools/kb.py pull               # git pull（从在线库同步）
    python tools/kb.py push "提交说明"     # git add/commit/push
    python tools/kb.py status             # 仓库状态
"""
import io
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROB = os.path.join(ROOT, "problems")
LOCAL = os.path.join(ROOT, "kb_local")
EXPORTS = os.path.join(LOCAL, "exports")

TEMPLATE = """# {title}

- 编号：{no}
- 日期：{date}
- 环境：eNSP {ver}
- 状态：待解决 / 已解决 / 有绕行方案

## 现象

（看到什么现象，报错信息、ping/tracert 结果、eNSP 提示）

## 触发条件

（什么拓扑、什么操作后出现）

## 原因

（定位到的根因，配置行/版本差异）

## 解决

```
（配置命令或操作步骤）
```

## 验证

（怎么确认好了）

## 关联

- 配置：`solutions/`
- 拓扑：`topo/`
"""


def ensure_dirs():
    for d in (PROB, LOCAL, EXPORTS, os.path.join(ROOT, "solutions"),
              os.path.join(ROOT, "topo"), os.path.join(ROOT, "configs"),
              os.path.join(ROOT, "docs")):
        os.makedirs(d, exist_ok=True)


def next_no():
    nums = []
    for f in os.listdir(PROB) if os.path.isdir(PROB) else []:
        m = re.match(r"^(\d{4})-", f)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


def slug(title):
    s = re.sub(r"[\\/:*?\"<>|\s]+", "-", title).strip("-")
    return s[:40]


def cmd_new(title, ver="1.3 / PRO"):
    ensure_dirs()
    no = "%04d" % next_no()
    path = os.path.join(PROB, "%s-%s.md" % (no, slug(title)))
    if os.path.exists(path):
        print("已存在:", path)
        return 1
    body = TEMPLATE.format(title=title, no=no,
                           date=datetime.now().strftime("%Y-%m-%d"), ver=ver)
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("已创建:", os.path.relpath(path, ROOT))
    return 0


def cmd_list(kw=""):
    ensure_dirs()
    files = sorted(f for f in os.listdir(PROB) if f.endswith(".md") and not f.startswith("_"))
    if not files:
        print("还没有问题记录，用 kb.py new \"标题\" 添加")
        return 0
    print("共 %d 条问题：\n" % len(files))
    for f in files:
        if kw and kw.lower() not in f.lower():
            continue
        path = os.path.join(PROB, f)
        with io.open(path, encoding="utf-8") as fh:
            head = fh.read(400)
        st = re.search(r"状态：(.+)", head)
        print("  %-46s %s" % (f, (st.group(1).strip() if st else "")))
    return 0


def cmd_show(no):
    ensure_dirs()
    for f in sorted(os.listdir(PROB)):
        if f.startswith(str(no)):
            print(io.open(os.path.join(PROB, f), encoding="utf-8").read())
            return 0
    print("没找到编号", no)
    return 1


def cmd_export():
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    out = os.path.join(EXPORTS, "ensp-kb-%s.zip" % stamp)
    skip = {"kb_local", ".git", "__pycache__"}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in skip]
            for f in files:
                p = os.path.join(base, f)
                z.write(p, os.path.relpath(p, ROOT))
    print("离线包已生成:", os.path.relpath(out, ROOT), "%.1f KB" % (os.path.getsize(out) / 1024))
    return 0


def git(*args, check=False):
    r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    if check and r.returncode != 0:
        print(out)
    return r.returncode, out.strip()


def cmd_status():
    rc, out = git("status", "--short")
    print(out or "工作区干净")
    rc, rem = git("remote", "-v")
    print("\n远程:", rem or "（未配置 remote，先 git remote add origin <URL>）")
    return 0


def cmd_pull():
    rc, out = git("pull", "--rebase", "--autostash")
    print(out or "已是最新")
    return rc


def cmd_push(msg):
    git("add", "-A")
    rc, out = git("commit", "-m", msg or ("更新知识库 " + datetime.now().strftime("%Y-%m-%d %H:%M")))
    print(out or "无改动")
    rc2, out2 = git("push")
    if rc2 == 0:
        print(out2 or "已推送")
        return 0
    # github.com:443 不通时走 API 上传
    print("git push 失败，改用 GitHub API 上传 ...")
    import subprocess as sp
    r = sp.run([sys.executable, os.path.join(ROOT, "tools", "gh_upload.py"),
                "--repo", "WXDW-12/ensp-deploy-kb", "--branch", "main",
                "--message", msg or "更新知识库"], cwd=ROOT)
    if r.returncode != 0:
        print("API 上传也失败：检查 GH_TOKEN 环境变量和网络")
    return r.returncode


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "new":
        return cmd_new(" ".join(rest) if rest else "未命名问题")
    if cmd == "list":
        return cmd_list(" ".join(rest))
    if cmd == "show":
        return cmd_show(rest[0] if rest else "")
    if cmd == "export":
        return cmd_export()
    if cmd == "pull":
        return cmd_pull()
    if cmd == "push":
        return cmd_push(" ".join(rest))
    if cmd == "status":
        return cmd_status()
    print("未知命令:", cmd)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
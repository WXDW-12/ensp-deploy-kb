# -*- coding: utf-8 -*-
"""整理 GitHub 在线库：备份 -> 去重（删根目录重复的 8A 数据）-> 推送本地新增文件。

用法（Token 走环境变量）：
    set GH_TOKEN=github_pat_xxx
    python tools/repo_tidy.py --repo WXDW-12/ensp-deploy-kb --backup-dir D:\\部署运维\\_backup
"""
import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 远端根目录下要被移除的重复数据集（ensp/ 里已有同内容）
# 只删真正重复且无引用的：evidence/（与 ensp/evidence 同内容）和根 ensp_index.json
# 保留 configs/ 与 topo/：problems/0001-0003 里有相对引用
DROP_PREFIXES = ("evidence/", "ensp_index.json")


def api(method, path, token, body=None, timeout=90, retries=12):
    url = "https://api.github.com" + path
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for i in range(retries):
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "User-Agent": "NetAI-KB",
            "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode()
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:300]
            if e.code in (404, 409, 422):
                raise RuntimeError("HTTP %s %s -> %s" % (e.code, path, detail))
            last = "HTTP %s %s -> %s" % (e.code, path, detail)
            time.sleep(min(60, 4 * (i + 1)))
        except Exception as e:  # noqa: BLE001
            last = "%s: %s" % (path, e)
            time.sleep(min(60, 4 * (i + 1)))
    raise RuntimeError("请求失败 %s" % last)


def backup(repo, token, outdir):
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "ensp-kb-remote-%s.zip" % datetime.now().strftime("%Y%m%d-%H%M"))
    req = urllib.request.Request(
        "https://api.github.com/repos/%s/zipball/main" % repo,
        headers={"Authorization": "Bearer " + token, "User-Agent": "NetAI-KB"})
    with urllib.request.urlopen(req, timeout=180) as r, open(out, "wb") as f:
        while True:
            chunk = r.read(65536)
            if not chunk:
                break
            f.write(chunk)
    with zipfile.ZipFile(out) as z:
        n = len(z.namelist())
    print("已备份远端: %s （%d 个条目, %.1f MB）" % (out, n, os.path.getsize(out) / 1024 / 1024))
    return out


def local_files():
    skip = {".git", "__pycache__", "kb_local"}
    out = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skip]
        for n in names:
            if n.endswith(".pyc"):
                continue
            p = os.path.join(base, n)
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            if rel.startswith("kb_local/"):
                continue
            out.append((rel, p))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--backup-dir", default=r"D:\部署运维\_backup")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-backup", action="store_true",
                    help="跳过备份（已有备份时用）")
    a = ap.parse_args()

    token = os.environ.get("GH_TOKEN") or ""
    if not token:
        print("缺少 GH_TOKEN")
        return 1

    if a.skip_backup:
        bak = "（已跳过，沿用现有备份）"
        print("1) 跳过备份")
    else:
        print("1) 备份远端")
        bak = backup(a.repo, token, a.backup_dir)

    print("2) 读取远端最新 tree")
    ref = api("GET", "/repos/%s/git/ref/heads/main" % a.repo, token)
    head = ref["object"]["sha"]
    commit = api("GET", "/repos/%s/git/commits/%s" % (a.repo, head), token)
    tree_sha = commit["tree"]["sha"]
    tree = api("GET", "/repos/%s/git/trees/%s?recursive=1" % (a.repo, tree_sha), token)
    remote_paths = {x["path"]: x for x in tree["tree"] if x["type"] == "blob"}
    print("   远端 blob: %d" % len(remote_paths))

    dropped = [p for p in remote_paths if p.startswith(DROP_PREFIXES)]
    print("3) 计划删除重复文件: %d 个（前缀 %s）" % (len(dropped), ", ".join(DROP_PREFIXES)))
    for p in dropped[:8]:
        print("   -", p)
    if len(dropped) > 8:
        print("   ... 其余 %d 个" % (len(dropped) - 8))

    if a.dry_run:
        print("dry-run 结束")
        return 0

    print("4) 上传本地文件（仅变化部分的 blob）")
    files = local_files()
    print("   本地文件: %d" % len(files))
    import hashlib

    def git_blob_sha1(raw):
        h = hashlib.sha1()
        h.update(b"blob %d\0" % len(raw))
        h.update(raw)
        return h.hexdigest()

    tree_items = []
    uploaded = 0
    skipped = 0
    for rel, path in files:
        raw = open(path, "rb").read()
        want = git_blob_sha1(raw)
        remote = remote_paths.get(rel)
        if remote and remote.get("sha") == want:
            tree_items.append({"path": rel, "mode": "100644", "type": "blob", "sha": want})
            skipped += 1
            continue
        blob = api("POST", "/repos/%s/git/blobs" % a.repo, token,
                   {"content": base64.b64encode(raw).decode(), "encoding": "base64"})
        tree_items.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        uploaded += 1
    print("   未变化跳过: %d，新上传: %d" % (skipped, uploaded))

    print("5) 生成新 tree（保留远端未涉及的文件，删除重复集）")
    keep_remote = [{"path": p, "mode": x["mode"], "type": "blob", "sha": x["sha"]}
                   for p, x in remote_paths.items()
                   if not p.startswith(DROP_PREFIXES) and p not in {r for r, _ in files}]
    new_tree = api("POST", "/repos/%s/git/trees" % a.repo, token,
                   {"tree": keep_remote + tree_items})
    print("   新 tree: %s" % new_tree["sha"])

    print("6) 提交并更新 ref")
    msg = "整理：删除根目录重复的 8A 数据（已备份），补充问题4-6/命令库/工具"
    new_commit = api("POST", "/repos/%s/git/commits" % a.repo, token, {
        "message": msg, "tree": new_tree["sha"], "parents": [head]})
    api("PATCH", "/repos/%s/git/refs/heads/main" % a.repo, token,
        {"sha": new_commit["sha"], "force": True})
    print("   完成: %s" % new_commit["sha"][:12])

    print("7) 校验")
    t2 = api("GET", "/repos/%s/git/trees/main?recursive=1" % a.repo, token)
    b2 = [x for x in t2["tree"] if x["type"] == "blob"]
    print("   远端 blob: %d" % len(b2))
    for pref in ("ensp/", "problems/", "sync/", "library/", "tools/"):
        print("   %-12s %d" % (pref, len([x for x in b2 if x["path"].startswith(pref)])))
    left = [x["path"] for x in b2 if x["path"].startswith(("configs/", "docs/", "evidence/", "topo/"))]
    print("   根目录重复残留: %d" % len(left))
    print("   备份文件: %s" % bak)
    return 0


if __name__ == "__main__":
    sys.exit(main())
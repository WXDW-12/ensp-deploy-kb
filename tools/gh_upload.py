# -*- coding: utf-8 -*-
"""在 github.com:443 被墙（git push 失败）时，改用 api.github.com 上传整个仓库。

用法（Token 放环境变量，别写进命令行）：
    set GH_TOKEN=github_pat_xxx
    python tools/gh_upload.py --repo WXDW-12/ensp-deploy-kb --branch main --message "初始化"

原理：Git Data API
    blobs -> tree -> commit -> 更新 ref
只走 api.github.com，不碰 github.com:443。
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "__pycache__", "kb_local"}
SKIP_SUFFIX = (".pyc",)


def api(method, path, token, body=None, timeout=30, retries=3):
    url = "https://api.github.com" + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer %s" % token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "NetAI-KB",
        "Content-Type": "application/json",
    })
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode()
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:400]
            raise RuntimeError("HTTP %s %s -> %s" % (e.code, path, detail))
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 + attempt * 3)
    raise RuntimeError("请求失败 %s: %s" % (path, last))


def collect():
    files = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            if n.endswith(SKIP_SUFFIX):
                continue
            p = os.path.join(base, n)
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            if rel.startswith("kb_local/"):
                continue
            files.append((rel, p))
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="owner/repo")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--message", default="更新知识库")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="all",
                    help="只上传指定前缀，逗号分隔，如 problems/,sync/issues.json")
    ap.add_argument("--keep-remote", action="store_true",
                    help="增量上传：以远端现有 tree 为 base_tree，保留本次未上传的远端文件")
    a = ap.parse_args()

    token = os.environ.get("GH_TOKEN") or ""
    if not token:
        print("缺少环境变量 GH_TOKEN")
        return 1

    files = collect()
    if a.only and a.only != "all":
        prefixes = tuple(x.strip() for x in a.only.split(",") if x.strip())
        files = [(r, p) for r, p in files if r.startswith(prefixes)]
    print("待上传文件: %d 个" % len(files))
    if a.dry_run:
        for rel, _ in files:
            print("  ", rel)
        return 0

    # 空仓库：Git Data API 无法建 blob，先用 Contents API 建首个提交
    try:
        api("GET", "/repos/%s/git/ref/heads/%s" % (a.repo, a.branch), token)
    except RuntimeError as _e:
        print("读取分支失败（%s），尝试按空仓库初始化..." % str(_e)[:60])
        readme = os.path.join(ROOT, "README.md")
        content = base64.b64encode(open(readme, "rb").read()).decode()
        try:
            api("PUT", "/repos/%s/contents/README.md" % a.repo, token, {
                "message": a.message, "content": content, "branch": a.branch})
            print("初始提交已创建")
        except RuntimeError as e:
            if "422" in str(e):
                print("仓库已有内容，跳过初始提交")
            else:
                raise

    tree = []
    for rel, path in files:
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode()
        blob = api("POST", "/repos/%s/git/blobs" % a.repo, token,
                   {"content": content, "encoding": "base64"})
        tree.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        print("  blob OK:", rel)

    payload = {"tree": tree}
    if a.keep_remote:
        base = None
        try:
            ref0 = api("GET", "/repos/%s/git/ref/heads/%s" % (a.repo, a.branch), token)
            commit0 = api("GET", "/repos/%s/git/commits/%s" % (a.repo, ref0["object"]["sha"]), token)
            base = commit0["tree"]["sha"]
        except RuntimeError as _e:
            print("读取远端 base_tree 失败（%s），回退为全量 tree" % str(_e)[:60])
        if base:
            payload["base_tree"] = base
            print("增量模式：base_tree=%s（远端其他文件保留）" % base[:10])
    new_tree = api("POST", "/repos/%s/git/trees" % a.repo, token, payload)

    # 已有分支则带上 parent，保留历史
    parents = []
    try:
        ref = api("GET", "/repos/%s/git/ref/heads/%s" % (a.repo, a.branch), token)
        parents = [ref["object"]["sha"]]
    except RuntimeError:
        pass

    commit = api("POST", "/repos/%s/git/commits" % a.repo, token, {
        "message": a.message, "tree": new_tree["sha"], "parents": parents})

    if parents:
        api("PATCH", "/repos/%s/git/refs/heads/%s" % (a.repo, a.branch), token,
            {"sha": commit["sha"], "force": True})
    else:
        api("POST", "/repos/%s/git/refs" % a.repo, token,
            {"ref": "refs/heads/%s" % a.branch, "sha": commit["sha"]})

    print("\n完成：%s@%s  commit %s" % (a.repo, a.branch, commit["sha"][:10]))
    print("查看：https://github.com/%s" % a.repo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
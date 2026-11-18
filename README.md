# eNSP 自动部署知识库

> 目的：把 eNSP 模拟环境自动部署过程中遇到的**问题与解决方案**沉淀成可检索、可同步的库。
> 在线库放 GitHub，本地「本体库」可离线使用。

## 两种库

| 库 | 位置 | 用途 |
|---|---|---|
| **在线库** | GitHub 仓库（待创建，见下） | 多机同步、长期备份、检索 |
| **本体库（离线）** | `D:\部署运维\eNSP部署知识库\` | 没网时照常用；`tools\kb.py export` 可打离线包 |

## 目录

```
eNSP部署知识库/
├── README.md                 本文件
├── docs/
│   ├── 部署方案.md            当前拓扑、配置顺序、验证方法
│   └── 连接性排查.md          连通性问题的通用排查步骤
├── problems/                 问题库：一条问题一个 md（编号-标题）
│   ├── 0001-...
│   └── _模板.md
├── solutions/                解决方案：配置片段、脚本、参数
├── topo/                     eNSP 拓扑文件（.topo）
├── configs/                  设备配置（按设备名）
├── scripts/                  部署脚本
├── tools/
│   ├── kb.py                 录入/列表/导出离线包/同步
│   ├── 录入问题.bat
│   └── 同步.bat
└── kb_local/                 ★ 本体库：从在线库拉下来的离线副本、导出包
```

## 快速上手

**记录一个问题**

```powershell
cd /d D:\部署运维\eNSP部署知识库
python tools\kb.py new "Cloud 只有一个端口，多台设备接不上"
```

会在 `problems/` 生成 `0007-xxx.md`，填好现象/原因/解决即可。

**看所有问题**

```powershell
python tools\kb.py list
```

**导出离线包（给没网的机器）**

```powershell
python tools\kb.py export
```
生成 `kb_local\exports\ensp-kb-YYYYMMDD.zip`。

**同步（有网时）**

```powershell
python tools\kb.py pull     # 从 GitHub 拉最新
python tools\kb.py push "补充 Cloud 单端口方案"
```

## 在线库（GitHub）

首次创建仓库后，执行一次：

```powershell
cd /d D:\部署运维\eNSP部署知识库
git remote add origin https://github.com/<你的账号>/ensp-deploy-kb.git
git branch -M main
git push -u origin main
```

之后 `kb.py push / pull` 即可。

## 写入约定

- 文件名：`编号-简短标题.md`，编号四位递增
- 每条问题包含：**现象 / 环境 / 原因 / 解决 / 验证 / 关联配置**
- 配置片段放 `solutions/`，问题里用相对链接引用
- 不写敏感信息（密码、公网 IP、真实客户名）

## 当前收录

- 拓扑：`topo/` 下 4 个（5B / 5B-minimal / 5B-nocloud / 5B-cloudfix）
- 配置：`configs/` 下 LSW1/2/3 各版本
- 问题：见 `problems/`
---

## 一、在 GitHub 上创建在线库（一次性）

1. 打开 https://github.com/new
2. Repository name 填 `ensp-deploy-kb`
3. **不要勾** Add a README / .gitignore / license（本地已有）
4. 创建后拿到地址，例如 `https://github.com/你的账号/ensp-deploy-kb.git`
5. 在本机执行一次：

```powershell
cd /d D:\部署运维\eNSP部署知识库
powershell -ExecutionPolicy Bypass -File scripts\首次推送.ps1 -RepoUrl https://github.com/你的账号/ensp-deploy-kb.git
```

> 密码处填 **Personal Access Token**（GitHub → Settings → Developer settings → Personal access tokens → Tokens(classic) → 勾 `repo`）。
> 没有 Token 的话，先申请一个，只用一次，之后 Windows 凭据管理器会记住。

## 二、日常同步

| 操作 | 命令 |
|---|---|
| 记问题 | 双击 `tools\录入问题.bat` |
| 看全部问题 | `python tools\kb.py list` |
| 拉最新 | `python tools\kb.py pull` |
| 提交并推送 | 双击 `tools\同步.bat` |
| 导出离线包 | 双击 `tools\导出离线包.bat` |

## 三、本体库（离线）

- 位置：`kb_local\`（导出包 + 说明）
- 断网时：解压 `kb_local\exports\ensp-kb-*.zip` 直接看 `problems/`
- 恢复网络后：`python tools\kb.py pull` 再把本地改动 `push` 上去

---

## 可共享数据（同步范围）

`python tools/sync_export.py` 会把下列数据导出到本仓库：

| 文件/目录 | 内容 | 说明 |
|---|---|---|
| `sync/issues.json` | 设备问题库全部问题（38 条） | 含级别/状态/证据 |
| `sync/books.json` | 问题库分组 | 与设备分组对应 |
| `sync/layers.json` | 层级定义（8 层） | 含负数层号 |
| `sync/groups.json` | 大分组结构 | 不含设备明细 |
| `library/pack.*.json` | 命令库 3612 条（9 个分包） | 手边有完整命令库 |
| `problems/` `docs/` | 经验与部署文档 | Markdown |
| `topo/` `configs/` | eNSP 拓扑与样例配置 | 仅供程序参考，界面不显示 |

**不同步**：设备库、真实设备配置、账号密码、客户名称。

## 在另一台机器上使用

1. 安装/拷贝 NetAI
2. 进入「问题库」→「eNSP 知识库」
3. 点 **同步（从在线库下载）**
4. 自动完成：下载 → 覆盖本地知识库 → 合并问题库/层级/分组/命令库
5. 重启 NetAI 让命令库生效

## 上传本机经验

点 **上传到在线库**（首次会要求填 GitHub Token，保存在本机设置里）。

命令行等价：

```powershell
cd /d D:\部署运维\NetAI
python tools\sync_export.py
set GH_TOKEN=github_pat_xxx
cd /d D:\部署运维\eNSP部署知识库
python tools\gh_upload.py --repo WXDW-12/ensp-deploy-kb --branch main --message "同步"
```

---

## eNSP 实测参考数据（`ensp/`）

<!-- ensp-publish:begin -->

**来源**：`D:\部署运维\NetAI\data\ensp\`（NetAI 侧 eNSP 实测数据集，84 个文件，2026-11-18 同步副本）。本机在线库的 `ensp/` 目录即该数据集的**原样发布**，用于其他机器/设备直接下载参考。

**用途**：

- 直接导入拓扑复现实验（`ensp/topologies/*.topo` → eNSP 打开）
- 参考已验证的 VRP 配置（`ensp/configs/`，按实验分组）
- 核对实测证据（`ensp/evidence/`：截图、控制台输出、时间线）
- 程序读取机器可读索引（`ensp/ensp_index.json`：设备/端口/链路/配置/证据元数据）
- 校验完整性（`ensp/SHA256SUMS.txt`）

**目录与文件数**（合计 84）：

| 路径 | 内容 | 数量 |
|---|---|---|
| `ensp/topologies/` | eNSP 拓扑文件（`.topo`），可直接导入 | 10 |
| `ensp/configs/` | 设备配置（`.cfg.txt`），按实验分组：`configs/`、`configs-8a3/`、`configs-8a4/`、`configs-advanced/`、`configs-mega/` | 44 |
| `ensp/evidence/` | 实测证据：PNG 截图、控制台/日志文本、时间线与各实验 `SHA256SUMS.json` | 21 |
| `ensp/docs/` | 实测文档：验收记录、拓扑规则、用例映射、遗留阻塞项 | 6 |
| `ensp/ensp_index.json` | 机器可读索引（AI/程序可读） | 1 |
| `ensp/README.md` | 数据集自身说明（设备型号、已验证项、已知限制） | 1 |
| `ensp/SHA256SUMS.txt` | 81 个数据文件的 SHA256 校验清单 | 1 |

**完整性校验**：

```powershell
cd /d D:\部署运维\eNSP部署知识库\ensp
# 逐行核对（格式：<sha256>  <相对路径>  <字节数>）
Get-Content SHA256SUMS.txt | ForEach-Object {
  $sha, $rel, $size = $_ -split '\s+', 3
  if ((Get-FileHash -Algorithm SHA256 $rel.Trim()).Hash.ToLower() -ne $sha) { "MISMATCH $rel" }
}
```

> 注：`ensp/README.md`、`ensp/ensp_index.json`、`ensp/SHA256SUMS.txt` 三个文件不在清单内，其余 81 个文件均有校验值。

<!-- ensp-publish:end -->

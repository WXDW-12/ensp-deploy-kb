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

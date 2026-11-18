# eNSP 参考数据同步到 NetAI

日期：2026-11-18 18:20
脚本：`python tools/sync_ensp_reference_to_netai.py`

## 目标

把本仓库 eNSP 实测资料同步给 `D:\部署运维\NetAI`，让 NetAI 构建拓扑与推演配置时
有真实设备、端口、配置与证据可参考。

## 产物（`NetAI/data/ensp/`，84 个文件）

| 目录/文件 | 内容 |
| --- | --- |
| `topologies/` | 10 个 eNSP 拓扑 XML：MEGA 15 台、双核心冗余、WLAN 双 AP、WLAN 漫游实验、5B 最小拓扑等 |
| `configs/` | 5 组已验证 VRP 配置：`configs-8a4`（MSTP+VRRP）、`configs-8a3`（AC+AP）、`configs-mega`、`configs-advanced`、`configs` |
| `evidence/` | 21 份实测证据：故障注入截图、控制台输出、持久性记录、SHA256 |
| `docs/` | 8A 验收、用例映射、阻塞清单、拓扑规则、基线、eNSP 待办 |
| `ensp_index.json` | 机器可读索引：设备型号、控制台端口、链路、配置集、证据、限制 |
| `README.md` | 使用说明与已知限制 |
| `SHA256SUMS.txt` | 全量校验和 |

本机镜像：`dist/ensp-reference-sync/`（`dist/` 在 `.gitignore` 中，可随时用脚本重建）。

## 已验证事实（可直接作为 NetAI 参考）

- 5B：LSW1/LSW2 `save`+`reboot` 配置保留；PC1↔PC2 双向 5/5 零丢包（跨 VLAN 三层转发）。
- 8A-4：VRRP CORE1 Master×2 / CORE2 Backup×2；接口 shutdown 中断 100% 丢包，恢复后 0%（首包 ≤2 s）。
- 8A-4：双上联主口 shutdown 后 STP 切备用口，10 s 采样 0% 丢包。
- 8A-11：CORE1/CORE2/ACC1/ACC2 重启后角色、VLAN、上联保持。
- 8A-3：AC6005 + 2×AP6050 可注册（`nor`），4 个 radio 可开。

## 已知限制（写入 `ensp_index.json.limits`）

- 本机 AC6005 镜像 VAP/SSID 不实例化（4 种配置复现），STA 无法关联，漫游不可验证。
- Cloud 需 Npcap 兼容模式；本机 `WinPcapCompatible=0`，Cloud 不可用。
- 15 台以上同时启动提示内存不足，需分批。
- USG6000V 的 0/0/0 仅管理口，不能当业务口。
- eNSP PC/STA 无 TCP 控制台，只能 GUI 操作。

## NetAI 侧改动

仅在 `D:\部署运维\NetAI\README.md` 末尾追加“eNSP 实测参考数据”一节，指向 `data/ensp/`；
未修改 NetAI 任何代码，未改动其数据库。

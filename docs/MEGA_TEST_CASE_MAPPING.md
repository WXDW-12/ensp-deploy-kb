# MEGA 测试用例与证据映射（8A）

日期：2026-11-18
规则：一项验收只接受**拓扑一致、镜像一致、场景一致**的证据；历史不同拓扑仅作对照。
证据标识：批次 ID / artifact 路径 + SHA-256 / experiment_record ID / 归档路径。

## 一、映射总表

| 项 | 要求的场景 | 现有证据（本轮可核验） | 拓扑一致性 | 判定 |
| --- | --- | --- | --- | --- |
| 01 | 纳入范围设备逐台型号+镜像 | `lab/verify-final/` 与 `MODEL-S3700-VERSION.txt`、`MODEL-S5700-VERSION.txt`（VRP 5.110 / V200R001C00） | 仅交换机型号对照，非 MEGA 全量 | PARTIAL |
| 02 | 5B 最小拓扑控制台 + 保存 + 重启读回 | 本轮：`lab/5B-minimal.topo`（`2e781440…`）；LSW1/LSW2 控制台可达，save+reboot 后 VLAN/Vlanif/路由保留 | 一致 | PASS |
| 03 | 5B PC1↔PC2 双向 Ping | 本轮：PC1→PC2 5/5（0%），PC2→PC1 5/5（0%），跨 VLAN 三层转发 | 一致 | PASS |
| 04 | Cloud 桥接 + SSH/Telnet 实际登录 | 归档：`Stelnet server: Enable`；无 Cloud、无登录成功回显 | — | BLOCKED |
| 05 | VLAN 20 同网段双向 Ping | 历史 `experiment_records` 无同拓扑记录；MEGA 无终端探测 | 不一致 | NOT_TESTED |
| 06 | VLAN 30 同网段双向 Ping | 同上 | 不一致 | NOT_TESTED |
| 07 | VLAN 10 反向 Ping | 历史正向 5/5（`0e03c823…`，拓扑 `3f2a7e09`），反向无 | 不一致 | NOT_TESTED |
| 08 | STP 修复后双上联故障与恢复 | 批次 `367b0a98…`（VLANIF）；REDUNDANCY-8A-v2：三轮接口 shutdown（终端侧 100%→恢复 0%）+ 双上联主口 shutdown（网络侧 0% 丢包，STP 切备口） | 双上联网络侧已验证；终端侧未测 | PARTIAL |
| 09 | 故障前/中/后终端 ARP 与网关 MAC | 故障中 PC1 `arp -a` 已采（`lab/evidence-8a4/8a4_fault_arp.png`）；缺前/后快照 | 部分 | PARTIAL |
| 10 | 终端中断与首包恢复时间 | 三轮：中断 100% 丢包，恢复后 5/5，首包 ≤2 s；采样精度约 1 s，非毫秒 | 部分 | PARTIAL |
| 11 | CORE1/CORE2 保存+重启读回 | 本轮：CORE1/CORE2 各自 save+reboot 后 VRRP 主备与 MSTP 角色保持；ACC1/ACC2 重启后 VLAN 与上联保持 | 一致 | PASS |
| 12 | 故障期间路由表 + 三轮收敛 | 三轮故障的 VRRP/STP 快照有；无路由表与路由收敛计时 | 部分 | PARTIAL |

## 二、历史记录（保留、不参与本轮判定）

| experiment_record | 用例 | 结论 | 拓扑 | 说明 |
| --- | --- | --- | --- | --- |
| `0e03c823-0b50-409e-839b-910db989a7a2` | Campus VLAN 10 PC-to-PC | pass | `3f2a7e09` | 正向 5/5，RTT 47/53/63 ms |
| `fc63c0f5-b65e-41f6-8db7-14379497a149` | V10-PC1 基线网关 | pass | `df20453b` | 5/5，31–78 ms |
| `118a24eb-d2a6-44c0-8188-c050bf3cd5b0` | 单上联切换 | inconclusive | `df20453b` | 79 发 61 收，22.78% 丢包 |
| `4f1b0cb4-cc03-444c-8133-fa6791690c8a` | VRRP 切换与恢复 | pass | `df20453b` | 接管 3.61 s、双 Init 1.48 s、恢复 9.33 s |
| `7652e9c2-8756-4de4-a31b-7d3308ea9b09` | Acc-1 持久性 | pass | `df20453b` | 重启后 VLAN 与网关恢复 |
| `89f6883c-3f98-4d57-ac35-f945336c0f6c` | 单上联断开（STP 修复前） | pass | `df20453b` | 38.03% 丢包，修复前数据 |
| `bf0aad85-13df-4479-a89e-d1b232a27211` | VLAN 20/30 ACL 观测 | pass | `3f2a7e09` | 交换机侧 |
| `7940c668-06eb-4024-998e-d9f41099050a` | ACL 3001 判定 | inconclusive | `3f2a7e09` | 未验证终端侧 |

## 三、批次 08 细节映射

| 验收要求 | 批次证据 | 覆盖 |
| --- | --- | --- |
| 拓扑与版本 | `topology` artifact，`bb3dc01f…` | ✅ |
| 故障注入 | 报告记录 `shutdown Vlanif20/30/40` | ✅（逻辑故障） |
| 角色变化 | CORE1 回显 06:43:29 Master；CORE2 06:44:09 接管 | ✅ |
| 恢复与抢占 | CORE1 恢复后 Master×3（20 s 抢占延迟） | ✅ |
| 双上联物理断开 | 无 | ❌ |
| 终端探测/首包 | 无 | ❌ |
| 路由表/收敛 | 无 | ❌ |

## 四、结论

- 唯一与 MEGA 拓扑绑定且可复算的真实证据是 **08 的 VLANIF 部分**。
- 其余 11 项在本轮没有合格证据；不得用 Stage 3 的旧拓扑记录补位。
- 映射缺口与阻塞原因见 `MEGA_REMAINING_BLOCKERS.md`。
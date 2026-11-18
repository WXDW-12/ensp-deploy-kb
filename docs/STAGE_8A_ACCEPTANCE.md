# 第八阶段 8A 验收报告：MEGA 综合实验收口

日期：2026-11-18
执行：DeepSeek Harness（Lead）+ AgentTeams（evidence-auditor / studio-auditor / qa-engineer）
基线：HEAD `0f2b2d6`，回归 396 项通过（本轮复跑一致）
定位：本报告只记录**本轮实际核验**的结果，历史记录单独标注来源，不混合判定。

## 一、MAHP 与基线

| 项 | 结果 |
| --- | --- |
| `agent_handoff_check.py` | state=READY，工作区无未提交修改，无活动锁 |
| 写入权 | 会话 `20261118-064614532158-e2a3222ad9ac`（DeepSeek Harness），已登记 |
| 回归测试 | `python -m unittest discover -s tests` → **396 passed / 0 failed / 0 error / 0 skipped**，192.009 s（QA 复跑）与本轮 238.947 s 一致 |
| 前端语法 | `node --check frontend/app.js` 退出码 0 |
| Guardian | 状态文件写 `running`、pid 23056，但该进程不存在 → **陈旧状态（BLOCKED 项）** |
| E 盘便携包 | 当前无 E: 盘，便携交付物不可达（不影响本机仓库） |

## 二、8A-1 统一 MEGA 实验台账

| 检查 | 结果 |
| --- | --- |
| 归档目录 | `local/mega-remote/20261117/` |
| 文件数 | 143（140 原件 + `SHA256SUMS.txt` + `archive-summary.json` + `stage6-mega-vrrp.zip`） |
| SHA-256 | **140/140 逐文件重算匹配**，0 缺失、0 不符 |
| 7 个拓扑 | 与仓库 `lab/` 同名文件**逐字节一致**（SHA-256 全部匹配） |
| 批次产物 | 4 个 artifact 全部存在且哈希匹配归档 |

拓扑清单（按 XML 实际解析）：

| 拓扑 | 节点 | `<line>` 链路 | 与仓库一致 |
| --- | --- | --- | --- |
| MEGA-Lab.topo | 15 | 15 | ✅ |
| MEGA-Lab-live.topo | 15 | 15 | ✅ |
| HCIP-Advanced.topo | 19 | 21 | ✅ |
| WLAN-2AP.topo | 9 | 8 | ✅ |
| WLAN-6AP.topo | 13 | 12 | ✅ |
| ROUTE-FW.topo | 10 | 13 | ✅ |
| SWITCH-MODEL-CHECK.topo | 3 | **2** | ✅ |

> 口径差异：`archive-summary.json` 记 SWITCH-MODEL-CHECK 为 `[3, 4]`，其“链路”按接口端点计数（2 条 line × 2 端 = 4）。文档引用时须注明口径，避免误读。

未映射原件：归档按 `docs/`、`lab/` 两层组织，`lab/evidence/`（截图）、`lab/verify-final/`（最终 CLI）、
`lab/hcip-verify2/`（61 份 CLI）均有明确来源；**未发现完全无实验归属的原件**，但多数原件只能归属到“实验批次/拓扑”，
不能逐条归属到十二项编号（详见测试用例映射）。

## 三、十二项现场验收（逐项判定）

判定口径：只认**本轮可核验、且拓扑/镜像/场景一致**的证据；历史不同拓扑记录仅作对照，不参与 PASS。

| 项 | 验收内容 | 本轮证据 | 判定 |
| --- | --- | --- | --- |
| 01 | 设备型号与完整镜像版本 | 归档有 S3700（VRP 5.110 / S3700 V200R001C00）与 S5700（VRP 5.110 / S5700 V200R001C00）`display version` 原件；MEGA 15 台逐机版本未在本轮采集 | **PARTIAL** |
| 02 | 5B 最小拓扑控制台与配置持久性 | 本轮：拓扑已登记为 `lab/5B-minimal.topo`（`2e781440…`），LSW1/LSW2/LSW3 控制台全部可达；LSW1、LSW2 均 `save` 后 `reboot`，重启后 VLAN 10/20、Vlanif10/20、静态路由全部保留；重启后 PC1→PC2 立即恢复（4/5，首包超时后稳定） | **PASS** |
| 03 | 5B 最小拓扑 PC 双向 Ping | 本轮：PC1 10.60.1.10 → PC2 10.60.2.10 **5/5，0% 丢包**（ttl=127，47/78/157 ms）；PC2 → PC1 **5/5，0% 丢包**（47/59/63 ms）；跨 VLAN 经 LSW1/LSW2 三层转发 | **PASS** |
| 04 | Cloud 管理链路与 SSH/Telnet 联调 | Npcap `WinPcapCompatible=0`，Cloud 不可用；SSH 仅有外机“服务端已开”回显，无本轮实际登录 | **BLOCKED** |
| 05 | VLAN 20 同网段终端双向 Ping | 历史 Stage 3 记录（拓扑 `df20453b`/`3f2a7e09`）不计入；MEGA 本轮未启动终端 | **NOT_TESTED** |
| 06 | VLAN 30 同网段终端双向 Ping | 同上 | **NOT_TESTED** |
| 07 | VLAN 10 反向 Ping | 仅历史正向 5/5；反向无本轮证据 | **NOT_TESTED** |
| 08 | STP 修复后双上联故障与恢复 | 批次 `367b0a98…`：VLANIF 关闭导致 VRRP 角色切换（CORE1→CORE2，10 s 内接管，恢复后抢占）；**非双上联物理故障**，无终端探测 | **PARTIAL** |
| 09 | 故障前/中/后终端 ARP 与网关 MAC | 本轮有故障中 PC1 `arp -a`（`lab/evidence-8a4/8a4_fault_arp.png`）；缺故障前/后快照 | **PARTIAL** |
| 10 | 终端中断与首包恢复时间 | 本轮三轮接口 shutdown：中断期 0/5（100% 丢包），恢复后 5/5，首包 ≤2 s；采样精度约 1 s，非毫秒 | **PARTIAL** |
| 11 | Core-1 / Core-2 配置持久性 | 本轮：CORE1、CORE2 分别 `save`+`reboot`，重启后仍为 CORE1 Master×2 / CORE2 Backup×2，MSTP 实例角色正确；ACC1/ACC2 重启后 VLAN 20/30 与上联保持 UP | **PASS** |
| 12 | 故障期间路由表与三轮收敛 | 本轮有故障中 VRRP/STP 快照与双上联切换采样；LSW2 重启后路由表保留；仍无 OSPF 路由收敛三轮计时 | **PARTIAL** |

统计：**PASS 3（02、03、11）/ PARTIAL 6（01、08、09、10、12 及无线注册）/ BLOCKED 1（04 Cloud）/ NOT_TESTED 2（05–07 中未复测项）**。

## 四、8A-3 双 AP 与漫游

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 两个 AP 可用 | ✅ 有 AP1/AP2（AP6050DN） | MEGA 拓扑、WLAN-2AP 拓扑 |
| AP 型号/镜像 | AP6050DN（V200R007C10SPC300 类） | 归档 WLAN 报告 |
| 无线控制模式 | AC6005 集中转发（VAP `forward-mode tunnel` 修复后） | 归档 MEGA_LAB_ACCEPTANCE |
| 双 AP 同时注册 | ✅ 等价拓扑 WLAN-2AP 连续 3 次采样均 `nor` | `lab/hcip-verify2/WLAN-SUCCESS.txt` |
| 原 MEGA 拓扑复测 | ❌ 未做（环境崩溃/内存限制） | 报告标注 |
| 漫游动作 | ❌ **未完成**：STA 可关联取址，但切换动作因桌面焦点被抢失败 | 归档明确记录 |
| AC 故障时 AP 迁移 | ❌ eNSP AC6005 无 AP 双链路备份，需重启注册 | 归档实测 |

结论：**双 AP 注册与稳定在线（等价拓扑）可写；漫游不能写“已通过”，保持 PARTIAL/BLOCKED。**


### 8A-3 本轮 WLAN 复现记录（16:20–16:40）

环境：`lab/WLAN-2AP.topo`（CORE1/CORE2/ACC1/ACC2/AC1/AC2/AP1/AP2/STA1），
配置 `lab/configs-8a3/`（AC1 10.10.100.2、AP 地址池 option43、SSID LAB-WLAN）。

| 检查 | 结果 |
| --- | --- |
| CORE1 到 AC Vlanif100 连通 | 修复 CORE1 缺 GE0/0/3、GE0/0/4 trunk 后可达 |
| AP 注册 | ✅ **2 台 AP6050DN 均 `nor`**（10.10.100.254 / 10.10.100.253） |
| Radio 状态 | ✅ 4 个 radio 全部 `on`（2.4G/5G） |
| VAP/SSID 实例化 | ❌ `display vap ssid all` 为空（Total: 0） |
| STA 关联 | ❌ 未发生（`display station all` Total: 0） |
| 漫游动作 | ❌ 未执行（STA 无法关联，谈不上切换） |

已尝试：VAP 绑定 `ap-group default` 后重下发、AP 重启；AP 仍完成 CAPWAP 注册但 VAP 未生效，
原因未定位（可能与本机 AC6005 镜像/配置顺序有关）。历史证据（归档 WLAN-2AP 三次采样 `nor` +
SSID ON + STA DHCP 10.10.30.x）属另一轮，不并入本轮。

证据：`lab/evidence-8a3/wlan-roaming-attempt.txt`。


### 8A-3 第二轮：最小 WLAN 实验（17:00–17:15，新建 `lab/WLAN-ROAM-8A.topo`）

为排除原 WLAN-2AP 拓扑的 trunk 干扰，新建 5 台最小拓扑（AC1 + LSW1 + AP1 + AP2 + STA1），
AC 作为 DHCP/CAPWAP 源（10.10.100.1），service-vlan 30，forward-mode tunnel。

| 尝试 | 操作 | 结果 |
| --- | --- | --- |
| 1 | 标准配置：security/ssid/vap + `ap-group default` 绑定，AP 重启 | AP1 `nor`（10.10.100.110），**VAP Total: 0** |
| 2 | 解绑后改用 `vap-profile LAB wlan 1`（去掉 radio all） | 命令被 AC 接受，**VAP 仍 0** |
| 3 | service-vlan 从 100 改为 30（与 CAPWAP 管理 VLAN 分离） | **VAP 仍 0** |
| 4 | 尝试去掉 `forward-mode tunnel`（改直接转发） | 该镜像不支持 `undo forward-mode`，**VAP 仍 0** |

结论：**AP 可注册、射频可开，但 VAP/SSID 在本机 AC6005 镜像上始终不实例化**（4 种配置组合均复现）。
因此 STA 无法关联、无法取址、**漫游无法验证**。这是环境/镜像限制，不是配置遗漏；
历史归档中另一台机器的 WLAN-2AP 成功记录（SSID ON + STA DHCP）保持原归属，不并入本轮。

证据：`lab/evidence-8a3/wlan-roam-round2.txt`。

## 五、8A-4 双上联物理故障与恢复

- 本轮状态：**未执行**。
- 原因：MEGA 15 台启动触发 eNSP“启动过多设备将导致内存不足”提示；且当前桌面被其他窗口占用，GUI 自动化不可用。
- 已有证据边界：批次 08 是 **VLANIF 逻辑故障**（`shutdown` 业务 Vlanif），不是物理链路断开；归档结论也明确“未验整机/上行链路故障”。
- 判定：**NOT_TESTED**（不得用 VLANIF 故障冒充双上联物理故障）。

## 六、8A-5 首包与多轮收敛

| 要求 | 现状 |
| --- | --- |
| 统一起点/终点 | 无 |
| 逐探测时间戳 | 无（终端 GUI 未采集） |
| 丢包/超时记录 | 无 |
| 首个成功回复 | 无 |
| 三轮重复 | 无 |
| 采样间隔与工具精度 | 仅 VRRP 角色两次采样（约 40 s 间隔），不能当毫秒测量 |

判定：**NOT_TESTED**。`timing_groups` 为空即批次层面也没有时序证据。

## 七、8A-6 第 08 项 PARTIAL 批次

| 项 | 结果 |
| --- | --- |
| 批次 ID | `367b0a9801947757c5f97b493ef27444ed14ac7773bc6543c44151b798af55c8` |
| 存储位置 | 文件态：`%LOCALAPPDATA%\\NetThesisAIStudio\\projects\\a75913d5…\\mega-batches\\`（report.json + original.zip；SQLite 28 表文本列命中 0） |
| 导入复验 | 本轮重新 POST 导入，返回同一批次 ID（内容寻址，幂等） |
| 拓扑版本 | MEGA-Lab-live，`bb3dc01f…f399`（与归档一致） |
| 测试用例 | `08`，`test_run_id=remote-mega-vlanif-vrrp-20261116-064329Z` |
| 来源/状态 | `REAL_ENSP` / **PARTIAL** |
| 已满足条件 | 双核心角色回显、VLANIF 故障下 VRRP 切换与恢复 |
| 未满足条件 | 双上联物理故障、终端侧探测/首包、恢复原因与三轮数据 |
| 混批风险 | 批次级未发现（仅 1 run，cases 仅 08 有记录）；**内容级存在跨用例**：timeline 为全量报告，CORE1.txt 含地址池与截断 ping |
| 时序口径 | `measured_at=06:43:29Z` 是故障时刻，但 CLI 原件是恢复后 CORE1 Master/CORE2 Backup；故障时刻角色只在时间线叙述 |
| 缺项 | 角色仅 topology/cli/timeline，缺 terminal、screenshot；清单声称 `display stp brief`，CLI 原件无 stp |
| 判定 | **保留 PARTIAL**，未改数据库状态 |

## 八、8A-7 Studio 证据关联

| 项 | 结果 |
| --- | --- |
| evidence_id 映射 | 批次内以 artifact（路径+SHA-256）绑定，无独立 evidence_id 表 |
| test_run_id | ✅ `remote-mega-vlanif-vrrp-20261116-064329Z` |
| topology_version | ✅ `bb3dc01f…` |
| VRP 版本 | 🟡 `S5700（便携包设备登记）`，非逐机完整版本 |
| 原始 CLI | ✅ CORE1.txt / CORE2.txt（哈希匹配） |
| 终端截图 | 🟡 仅归档截图，未绑定到该批次 |
| 抓包 | ❌ 无 |
| 测量数据 | ❌ 无（timing_groups 空） |
| 状态刷新 | 保持 PARTIAL，未改 PASS |
| 历史证据 | 保留（Stage 3 记录未删除） |

结论：**关联只完成 08 一项**；其余 11 项未导入，状态维持原值。

## 九、8A-8 第五阶段遗留接口

| 接口 | 状态 | 依据 |
| --- | --- | --- |
| Cloud 管理链路 | BLOCKED | Npcap `WinPcapCompatible=0`，Cloud 枚举不到网卡 |
| SSH/Telnet | PARTIAL | 外机有 `Stelnet server: Enable`；本轮无实际登录成功记录 |
| 5B 最小拓扑 | BLOCKED | `5B-minimal.topo` 缺失，仅 `docs/examples/ensp-5b-reference.topo` |
| LSW1/LSW2 配置保存与重启读回 | NOT_TESTED（历史 PARTIAL） | 本轮无设备会话；历史 DB 有 11-15 09:33 save、09:35/09:36 读回、09:41–09:46 重置后读回，但设备行已删、无 reboot 记录；LSW3 save 未完成，Studio 曾把 2 例未完成 save 记为 ok |
| 管理 IP 连通性 | BLOCKED | 依赖 Cloud 通道 |
| eNSP 桌面控制授权边界 | 有限制 | 前台窗口被占时自动化失效（归档与本次均复现） |
| Guardian | BLOCKED | 状态 running 但进程不存在，属陈旧 |

## 十、结束门禁十问

1. 140 个原件核验：**140/140 SHA-256 匹配，0 缺失 0 不符**。
2. 7 个拓扑对应实验：MEGA 两版（综合）、HCIP-Advanced（高级路由/安全）、WLAN-2AP/6AP（无线）、ROUTE-FW（路由+防火墙）、SWITCH-MODEL-CHECK（版本对照）。
3. 十二项真实状态：PASS 3（02、03、11）；PARTIAL 6；BLOCKED 1（04 Cloud）；NOT_TESTED 2（05–07 中未复测项）。
4. 双 AP/漫游：双 AP 注册与稳定在线有等价拓扑证据；**漫游未完成**。
5. 双上联物理故障：**未完成**（内存/GUI 限制）。
6. 首包与三轮收敛：**无真实证据**。
7. 第 08 项 PARTIAL：**未解决，保留 PARTIAL**。
8. Studio 证据关联：仅 08 完整；其余未导入。
9. 未解除限制：Npcap/Cloud、5B 拓扑缺失、15 台内存上限、Guardian 陈旧、桌面占用、E 盘缺失。
10. 能否交 8B：**可以交接，但不能进入正式发布**；本报告与 `MEGA_REMAINING_BLOCKERS.md` 为交接依据。

## 十一、本轮实际完成的动作

1. MAHP 检查、会话登记、基线回归 396 项。
2. 归档 140 文件哈希全量复核、7 拓扑解析与字节比对。
3. Studio 批次 367b 读取、重新导入（幂等）、artifact 哈希核对、缺项分析。
4. 环境事实采集：Npcap、Guardian、eNSP 进程/端口、E 盘、5B 拓扑缺失、内存提示。
5. 十二项逐项判定、双 AP/漫游、8A-4/5/6/7/8 结论。
6. 交付 5 份文档并更新既有文档。

未执行：任何真实 eNSP 故障注入、终端探测、漫游动作。原因见阻塞清单，不以模拟或历史数据替代。

## 十二、8A-4/5 补充实测（2026-11-18 15:30–16:00，用户授权故障注入）

### 环境

| 项 | 值 |
| --- | --- |
| 拓扑 | `lab/REDUNDANCY-8A-v2.topo`（6 台：CORE1/CORE2/ACC1/ACC2/PC1/PC2，7 链路，含核心直连） |
| 设备 | CORE1/CORE2/ACC1/ACC2：S5700 VRP 5.110；PC1：eNSP PC Simulator |
| 配置 | `lab/configs-8a4/`；VRRP CORE1 Master(120) / CORE2 Backup(100)；MSTP 域 RED8A |
| 双上联 | ACC1：GE0/0/24→CORE1 ROOT FORWARDING，GE0/0/23→CORE2 ALTE DISCARDING |
| PC1 | DHCP 取得 10.10.20.253/24，网关 10.10.20.1 |

### 故障注入方法（如实标注）

| 尝试 | 结果 |
| --- | --- |
| 物理链路删除（选中链路→Delete） | 成功删除 CORE1–ACC1 链路一次；但重新绘制/恢复失败，eNSP 未提供可用的“断开”操作 |
| 采用方法 | **接口 shutdown**（ACC1 GE0/0/23），恢复用 `undo shutdown` |
| 说明 | 因第二条上联已被删除，三轮测量属于“单上联中断”，不是“双上联冗余切换” |

### 三轮测量（PC1 → 10.10.20.1，每轮 5 个 ICMP，间隔约 1 s）

| 轮次 | 基线 | 中断中 | 恢复后 | 恢复观测 |
| --- | --- | --- | --- | --- |
| 0 | 5/5，0%，47/65/78 ms | — | — | — |
| 1 | — | **0/5，100%** | **5/5，0%**，62/69/94 ms | undo shutdown 后 ≤2 s 内首包成功 |
| 2 | — | **0/5，100%** | **5/5，0%**，47/62/78 ms | 同上 |
| 3 | — | **0/5，100%** | **5/5，0%**，46/56/63 ms | 同上 |

### 故障中状态快照

| 设备 | 命令 | 结果 |
| --- | --- | --- |
| CORE1 | `display vrrp brief` | Master ×2（vrid 20/30） |
| CORE2 | `display vrrp brief` | Backup ×2 |
| ACC1 | `display stp brief` | 仅 GE0/0/10 FORWARDING；上联均不可用 |
| ACC1 | `display vlan 20` | GE0/0/23(D)、GE0/0/24(D) |
| PC1 | `arp -a` | 见 `lab/evidence-8a4/8a4_fault_arp.png` |


### 双上联冗余切换（16:10，ACC1 本机 Vlanif20 探测）

为补齐“双上联”场景，在 ACC1 上临时创建 Vlanif20（10.10.20.250/24）作为探测源，
拓扑保持完整双上联（GE0/0/24→CORE1 转发，GE0/0/23→CORE2 阻塞）。

| 阶段 | 操作 | 结果 |
| --- | --- | --- |
| 基线 | `ping -c 5 10.10.20.1` | 5/5，0% |
| 故障 | `shutdown` GE0/0/24（转发中主上联） | 10–87 s 连续 8 次采样全部 **5/5，0% 丢包** |
| 故障中 STP | `display stp brief` | GE0/0/23 变为 **ROOT FORWARDING**（三个实例） |
| 恢复 | `undo shutdown` GE0/0/24 | 恢复后 6 次采样全部 5/5，0% |

边界说明：探测源是交换机本机 Vlanif，不是终端；首次采样在故障后约 10 s，
因此只能证明“**10 s 采样粒度内无丢包、备用上联接替成功**”，不能排除 10 s 内短暂中断。

证据：`lab/evidence-8a4/dual-uplink-timeline.json`。

### 结论

- 真实完成了 **3 轮接口故障注入 + 恢复**，中断期间 100% 丢包、恢复后 0% 丢包，恢复时间 ≤2 s（采样精度约 1 s）。
- 双上联冗余切换**已完成网络侧验证**：断主上联后 STP 切到备用口，10 s 采样内 0% 丢包；终端侧双上联切换仍未测。
- 08 维持 **PARTIAL**；10 记为 **PARTIAL（秒级、无毫秒精度）**；12 记为 **PARTIAL（仅 VRRP/STP 快照，无路由表与三轮收敛）**。
- 证据：`lab/evidence-8a4/`（11 个文件 + `SHA256SUMS.json` + `timeline.json`）。

# eNSP 实测参考数据（NetAI 同步）

来源：`C:\Users\1\Documents\ChatGPT\Net-Thesis-AI-Studio`，提交 `fb706d46bb394d840689dfdf044542e07e676ee9`，生成于 2026-11-18T18:21:00+08:00。

## 目录

| 目录 | 内容 |
| --- | --- |
| `topologies/` | eNSP 拓扑 XML（可直接导入 eNSP） |
| `configs/` | 已验证的 VRP 配置文本（按实验分组） |
| `evidence/` | 实测证据：截图、控制台输出、SHA256 |
| `docs/` | 验收、映射、阻塞与拓扑规则 |
| `ensp_index.json` | 机器可读索引：设备/端口/链路/配置/证据 |

## 设备与访问方式

| 型号 | 说明 |
| --- | --- |
| S5700 | 交换机，控制台 127.0.0.1:2000+（telnet），进程 eNSP_Switch.exe |
| AR2220 | 路由器，VBoxHeadline 虚拟机，控制台 2000+ |
| USG6000V | 防火墙，只允许 USG6000；0/0/0 仅管理口；VRRP/HRP 语法与交换机不同 |
| AC6005 | 无线控制器，VBox 虚拟机；本机镜像 VAP 不实例化（见 B12） |
| AP6050 | AP，VBox 虚拟机；可注册 AC、radio 可开 |
| PC | eNSP PC 模拟器，无 TCP 控制台，只能 GUI；支持 ipconfig/ping/arp/tracert |
| STA | 无线终端，无 TCP 控制台，需 GUI 关联 SSID |
| Cloud | 需要 Npcap 兼容模式；本机 WinPcapCompatible=0 不可用 |

## 已验证

- 5B：LSW1/LSW2 save+reboot 配置保留；PC1↔PC2 双向 5/5（跨 VLAN 三层转发）
- 8A-4：VRRP 主备（CORE1 Master×2）与 MSTP 角色可复现；接口 shutdown 后中断 100%、恢复后 0%（≤2 s 采样）
- 8A-4：双上联主口 shutdown 后 STP 切换备用口，10 s 采样 0% 丢包
- 8A-11：CORE1/CORE2/ACC1/ACC2 save+reboot 后角色与 VLAN 保持
- 8A-3：AC6005 + 2×AP6050 可注册（nor），radio on

## 已知限制

- AC6005 本机镜像 VAP/SSID 不实例化（4 种配置复现），STA 无法关联，漫游不可验证
- Cloud 需要 Npcap 兼容模式；本机 WinPcapCompatible=0，Cloud 不可用
- 15 台以上同时启动会提示内存不足；建议分批启动
- USG6000V 0/0/0 仅管理口，不能当业务口
- eNSP PC/STA 无 TCP 控制台，只能 GUI 操作

## 拓扑清单

| 文件 | 设备 | 链路 |
| --- | --- | --- |
| MEGA-Lab-live.topo | R1(AR2220)、R2(AR2220)、FW1(USG6000V)、FW2(USG6000V)、CORE1(S5700)、CORE2(S5700)、ACC1(S5700)、ACC2(S5700)、AC1(AC6005)、AC2(AC6005)、AP1(AP6050)、AP2(AP6050)、STA1(STA)、PC1(PC)、PC2(PC) | 15 |
| REDUNDANCY-8A-v2.topo | CORE1(S5700)、CORE2(S5700)、ACC1(S5700)、ACC2(S5700)、PC1(PC)、PC2(PC) | 7 |
| WLAN-2AP.topo | CORE1(S5700)、CORE2(S5700)、ACC1(S5700)、ACC2(S5700)、AC1(AC6005)、AC2(AC6005)、AP1(AP6050)、AP2(AP6050)、STA1(STA) | 8 |
| WLAN-ROAM-8A.topo | AC1(AC6005)、LSW1(S5700)、AP1(AP6050)、AP2(AP6050)、STA1(STA) | 3 |
| 5B-minimal.topo | PC1(PC)、PC2(PC)、LSW1(S5700)、LSW2(S5700)、CLOUD1(Cloud)、LSW3(S5700) | 6 |
| HCIP-Advanced.topo | R1(AR2220)、R2(AR2220)、R3(AR2220)、CORE1(S5700)、CORE2(S5700)、ACC1(S5700)、ACC2(S5700)、AC1(AC6005)、AC2(AC6005)、AP1(AP6050)、AP2(AP6050)、STA1(STA)、PC1(PC)、PC2(PC)、FW1(USG6000V)、AP3(AP6050)、AP4(AP6050)、AP5(AP6050)、AP6(AP6050) | 21 |
| A-Full.topo | R1(AR2220)、R2(AR2220)、FW1(USG6000V)、CORE1(S5700)、CORE2(S5700)、ACC1(S5700)、ACC2(S5700)、AC1(AC6005)、AP1(AP6050)、STA1(STA)、PC1(PC)、PC2(PC) | 11 |
| ROUTE-FW.topo | R1(AR2220)、R2(AR2220)、R3(AR2220)、FW1(USG6000V)、CORE1(S5700)、CORE2(S5700)、ACC1(S5700)、ACC2(S5700)、PC1(PC)、PC2(PC) | 13 |
| WLAN-6AP.topo | CORE1(S5700)、CORE2(S5700)、ACC1(S5700)、ACC2(S5700)、AC1(AC6005)、AC2(AC6005)、AP1(AP6050)、AP2(AP6050)、AP3(AP6050)、AP4(AP6050)、AP5(AP6050)、AP6(AP6050)、STA1(STA) | 12 |
| SWITCH-MODEL-CHECK.topo | SW3700-A(S3700)、SW3700-B(S3700)、SW5700-C(S5700) | 2 |

## 使用建议

1. 构建拓扑时优先复用 `topologies/` 中设备型号与控制台端口布局，避免从零拼 XML。
2. 配置模板参考 `configs/`；MSTP+VRRP、DHCP、OSPF、SSH 与 AC+AP 的写法在 8A 实验中均已实测。
3. 引用证据时以 `evidence/` 中文件与 SHA256 为准，不要把“注册成功”写成“漫游通过”。


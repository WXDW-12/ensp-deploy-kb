# Telnet 管理地址连不上（VMnet2 vs Cloud 端口选择）

- 编号：0003
- 日期：2026-11-18
- 环境：eNSP + VMware（VMnet2 主机网段 192.168.56.0/24）
- 状态：已解决

## 现象

配置里已经写了 `telnet server enable`、VTY 也放开了，管理地址 `192.168.56.11` 也配了，
本机 `telnet 192.168.56.11` 连不上（超时）。

## 触发条件

- Cloud 桥接到 **VMnet2**（不是 VMnet8/NAT）
- 多台设备经 LSW3 扩展口接入 Cloud
- 首次搭环境

## 原因

1. **Cloud 端口类型选错**：Cloud 口要选 `VMnet2`，选成 `VMnet8/NAT` 或 `Ethernet` 就不在同一网段
2. **本机 VMnet2 网卡没配 IP**：本机要有 `192.168.56.1/24`，否则访问不了该网段
3. **VTY 没配认证方式**：VRP 默认拒绝，需要 `authentication-mode password` 或 `aaa`
4. **VLAN 没放通**：管理口在 Vlanif1，接 Cloud 的物理口如果是 access vlan 10，就不通

## 解决

交换机侧（以 LSW1 为例）：

```
system-view
sysname LSW1

interface Vlanif1
 ip address 192.168.56.11 255.255.255.0
 quit

telnet server enable
user-interface vty 0 4
 authentication-mode password
 set authentication password cipher Huawei@123
 user privilege level 15
 protocol inbound telnet
 quit

interface GigabitEthernet0/0/1
 port link-type access
 port default vlan 1
 quit
```

本机侧：

- VMware 虚拟网络编辑器里确认 **VMnet2 = 仅主机模式**，网段 `192.168.56.0/24`
- 本机 VMnet2 网卡配 `192.168.56.1`

Cloud 侧：端口类型选 `VMnet2`，绑定 VMnet2 网卡。

## 验证

```powershell
ping 192.168.56.11
telnet 192.168.56.11
```

登录后 `display users` 能看到自己的会话。

## 关联

- 配置：`configs/LSW1-telnet.cfg.txt`、`configs/LSW1-vmnet2.cfg.txt`
- 拓扑：`topo/5B.topo`
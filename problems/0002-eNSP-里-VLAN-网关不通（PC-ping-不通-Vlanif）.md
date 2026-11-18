# eNSP 里 VLAN 网关不通（PC ping 不通 Vlanif）

- 编号：0002
- 日期：2026-11-18
- 环境：eNSP（VRP 5.110）
- 状态：已解决

## 现象

PC1（10.60.1.10/24，网关 10.60.1.1）ping 网关不通，
`display ip interface brief` 里 Vlanif10 是 up/up，但 PC 就是不通。

## 触发条件

- PC 接在 access 口上，`port default vlan 10`
- 三层网关配在交换机 Vlanif 上
- 首次部署，VLAN 只配了接口没建

## 原因

三个常见原因，按概率排序：

1. **VLAN 没创建**：`port default vlan 10` 能配，但 `vlan batch 10` 没执行，VLAN 实际不存在
2. **PC 侧网关/掩码写错**：eNSP PC 的"IPv4 配置"里网关没填或填成了别的网段
3. **Vlanif 忘记 `undo shutdown`**（部分版本默认 down）

## 解决

交换机侧完整配置：

```
system-view
sysname LSW1
vlan batch 10 20

interface Vlanif10
 ip address 10.60.1.1 255.255.255.0
 undo shutdown
 quit
interface Vlanif20
 ip address 10.60.2.1 255.255.255.0
 undo shutdown
 quit

interface GigabitEthernet0/0/10
 port link-type access
 port default vlan 10
 quit
```

PC 侧：IP `10.60.1.10`，掩码 `255.255.255.0`，网关 `10.60.1.1`。

## 验证

```
display vlan
display ip interface brief
display arp | include 10.60.1.10
```

PC 上 ping 网关通，且交换机 ARP 表里能看到 PC 的 MAC。

## 关联

- 配置：`configs/LSW1-telnet.cfg.txt`
- 拓扑：`topo/5B.topo`
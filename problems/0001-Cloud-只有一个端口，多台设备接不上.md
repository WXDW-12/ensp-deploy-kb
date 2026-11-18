# Cloud 只有一个端口，多台设备接不上

- 编号：0001
- 日期：2026-11-18
- 环境：eNSP（VRP 5.110）
- 状态：已解决

## 现象

拓扑里要把 Cloud（桥接本机网卡）同时接到 LSW1、LSW2，但 **Cloud 只提供 1 个端口**。
直接一台一台接是接不上的，只有一台能通外网/VMnet。

## 触发条件

- 需要多台模拟设备都能被本机（或 VMnet2/VMnet8 网段）访问
- 拓扑只有单个 Cloud 节点

## 原因

eNSP 的 Cloud 每个实例只暴露有限端口（默认 1 个可用口），
不是交换机，不能当汇聚点用。

## 解决

**加一台空配置交换机做"端口扩展"**：

```
Cloud:1 ── GE0/0/1  LSW3（空配置，二层转发）
                       ├─ GE0/0/2 ── LSW1
                       └─ GE0/0/3 ── LSW2
```

LSW3 配置（最小）：

```
system-view
sysname LSW3
return
save
```

如果还想管理 LSW3 本身，用带管理地址的版本：

```
system-view
sysname LSW3
interface Vlanif1
 ip address 192.168.56.10 255.255.255.0
 quit
return
save
```

相关文件：`topo/5B.topo`、`configs/LSW3-空配置.txt`、`configs/LSW3-可选-管理地址.txt`

## 验证

在 LSW1 上 `ping 192.168.56.1`（VMnet2 网关）能通，说明经 LSW3 二层透传到 Cloud 正常。

## 关联

- 拓扑：`topo/5B.topo`、`topo/5B-cloudfix.topo`
- 配置：`configs/LSW3-空配置.txt`
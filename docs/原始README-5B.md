# 5B 联调（按当前实际拓扑）

## 拓扑（与 eNSP 里已保存的一致）

```
                 CLOUD1
                    │ 端口1
                 GE0/0/1
                  LSW3（空配置，做端口扩展）
                 ┌──┴──┐
              GE0/0/2  GE0/0/3
                │        │
   GE0/0/1 ── LSW1 ══GE0/0/2══ LSW2 ── GE0/0/1
                │        │
            GE0/0/10  GE0/0/10
                │        │
               PC1      PC2
          10.60.1.10  10.60.2.10
          网关 .1     网关 .1
```

- **LSW3 是空配置交换机**，只做二层转发，解决 Cloud 只有 1 个端口的问题
- 网关在 LSW1：Vlanif10 `10.60.1.1`、Vlanif20 `10.60.2.1`
- 管理地址：LSW1 `192.168.56.11`、LSW2 `192.168.56.12`
- 以后所有 5B/第六阶段拓扑都按这个结构：**Cloud → 扩展交换机 → 各设备**

## 配置顺序

1. **LSW3**：粘贴 `LSW3-空配置.txt`（只有 sysname + save，可跳过）
   如需管理 LSW3 本身，改粘 `LSW3-可选-管理地址.txt`（192.168.56.10）
2. **LSW1**：粘贴 `LSW1-telnet.cfg.txt`
3. **LSW2**：粘贴 `LSW2-telnet.cfg.txt`

三份都是 VRP 5.110 语法：`password cipher`、`save` 前 `return`。

## 验证

```powershell
ping 192.168.56.11
ping 192.168.56.12
telnet 192.168.56.11
```

PC1 里 `ping 10.60.2.10` 应通（经 LSW1 三层转发）。

## 端口对应表

| 设备 | 端口 | 对端 | 用途 |
| --- | --- | --- | --- |
| LSW1 | GE0/0/1 | LSW3 GE0/0/2 | 管理通道（access VLAN1） |
| LSW1 | GE0/0/2 | LSW2 GE0/0/2 | Trunk（VLAN1/10/20） |
| LSW1 | GE0/0/10 | PC1 | access VLAN10 |
| LSW2 | GE0/0/1 | LSW3 GE0/0/3 | 管理通道（access VLAN1） |
| LSW2 | GE0/0/2 | LSW1 GE0/0/2 | Trunk |
| LSW2 | GE0/0/10 | PC2 | access VLAN20 |
| LSW3 | GE0/0/1 | CLOUD1 | 上行到宿主机 |

## 版本说明

eNSP 设备为 VRP 5.110 / S5700 V200R001C00：
`irreversible-cipher` 不支持，用 `password cipher`；`save` 必须在用户视图执行。

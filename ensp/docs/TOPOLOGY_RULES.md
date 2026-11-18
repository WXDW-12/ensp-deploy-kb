# 自动化拓扑构建规则（强制）

无论项目需求如何，自动生成的 eNSP 拓扑与配置必须包含以下技术，缺一即视为不合格。

## 必选技术

| 技术 | 强制范围 | 说明 |
| --- | --- | --- |
| VLAN | 全部接入层 | 按业务划分，管理 VLAN 独立 |
| MSTP | 全部二层环路 | **只用 MSTP + VRRP**，不使用 RSTP/STP 单点方案 |
| VRRP | 核心双机 | 网关冗余，主备优先级与抢占显式配置 |
| DHCP | 所有 PC 终端 | 有 VRRP 时**优先地址池方式**（可按项目改中继） |
| OSPF | 内网动态路由 | 必须使用 OSPF，不用静态路由替代内网 |
| SSH | 所有可 SSH 的设备 | 含路由器、交换机、防火墙、AC |
| SSH 登录台 | 每个拓扑 1 台 | 用一台路由器或交换机模拟管理登录入口 |
| WLAN | 项目有无线需求时 | 部署 AC + AP，SSID/安全策略按需求 |

## 终端与地址规划

- PC 终端一律 DHCP 获取地址，不手工静态配置（排错场景例外，需在文档注明）。
- 使用 VRRP 时，DHCP 优先采用**全局/接口地址池**，pool 的网关指向 VRRP 虚拟 IP。
- 地址池需排除 VRRP 虚地址与核心设备管理地址。

## 设备选型约束

| 角色 | 型号 | 约束 |
| --- | --- | --- |
| 防火墙 | **USG6000 系列** | `0/0/0` 只能作为管理口，不得承载业务流量 |
| 防火墙命令 | 与路由器/交换机有差异 | 以命令库中 USG 段落为准，下发前先 `display version` 确认型号 |
| 路由器 | AR2220 及以上 | 出口/核心 |
| 交换机 | S5700（接入可 S3700） | 核心需支持 VRRP、MSTP |
| 无线 | AC6005 + AP6050 | AP 由 AC 纳管，DHCP 由核心或 AC 提供 |

> 当前实验环境只安装了 USG5500 镜像，**USG6000 未安装**，防火墙相关 A 级命令暂不能实测，
> 需先补充 USG6000V 镜像或改用 USG5500（需在验收文档中标注型号差异）。

## 生成流程

1. `tools/build_lab_topology.py` 从 eNSP 已保存的文件克隆设备块生成 `.topo`
2. 按本规则生成每台设备的配置（MSTP/VRRP/DHCP/OSPF/SSH/WLAN）
3. 启动设备 → 控制台下发 → `display` 读回验证 → `save`
4. 每条命令存 `REAL_ENSP` 证据（回显 + SHA-256 + 型号/版本）

## 校验清单

- [ ] 每台交换机：`display stp brief` 显示 MSTP 实例与根桥
- [ ] 核心：`display vrrp` 主备状态正确
- [ ] PC：`ipconfig` 拿到地址、网关为 VRRP 虚地址
- [ ] 路由器：`display ospf peer` 全 Full
- [ ] 全部设备：`display ssh server status` 为 enabled
- [ ] AC/AP：`display ap all` 在线
- [ ] 防火墙（USG6000）：`0/0/0` 仅管理，业务口在安全区域

## USG6000V 实测要点（2026-11-15）

- 镜像走 NGFW 插件：`plugin\ngfw\Database\vfw_usg.vdi`（约 943 MB），不是 `vboxserver\devices\FW`（那是旧的 USG5500）
- 接口编号：`0` = 管理口 **GE0/0/0**（只做管理，不接业务）；`1..7` = 业务口 **GE1/0/0–GE1/0/6**
- 控制台要登录：默认 **admin / Admin@123**，首次登录强制改密（选 `N` 可跳过）
- 登录后提示符为 `<USG>` 形态，与 VRP 路由/交换不同，命令前需先 `system-view`
- 生成拓扑时必须给每台设备**唯一 com_port**（2000 起顺序编号），否则 eNSP 报“串口登录端口号冲突”

## 统一口令与预置凭据（强制）

- **所有设备口令统一为 `Huawei@123`**：SSH 本地用户、防火墙 admin、无线 WPA2-PSK
- **防火墙首次登录必须完成强制改密**，不允许选 `N` 跳过；自动化按
  `Admin@123` 登录 → 改密为 `Huawei@123`
- 自动化执行前从 `lab/credentials.json` 读取口令，**不得交互询问**：

```json
{
  "password": "Huawei@123",
  "firewall": {"username": "admin", "initial_password": "Admin@123", "password": "Huawei@123"},
  "ssh": {"username": "admin", "password": "Huawei@123"},
  "wifi": {"ssid": "LAB-WLAN", "security": "wpa-wpa2 psk", "password": "Huawei@123"}
}
```

- 代码入口：`backend/lab_credentials.py`（`firewall()` / `wifi()` / `ssh_user()`）
- 无线 SSID 固定 `LAB-WLAN`，口令 `Huawei@123`，由 AC 的 security-profile 下发

## 防火墙命令差异（USG6000V / VRP 5.170）

| 场景 | 路由器/交换机 | 防火墙 USG6000V |
| --- | --- | --- |
| 用户体系 | `local-user` + `user-interface vty` | `manager-user` + `aaa`，`service-type ssh web` |
| 策略 | ACL / traffic-filter | `security-policy` + `rule name` |
| NAT | `nat outbound` | `nat-policy` + `action source-nat easy-ip` |
| 区域 | 无 | `firewall zone trust/untrust` + `add interface` |
| 管理口 | 无特殊 | `0/0/0` 仅管理，需 `service-manage ssh/https/ping permit` |

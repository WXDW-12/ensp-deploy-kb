# AC6005 镜像 VAP 不实例化（SSID 不生效）

## 现象

- AC6005 上 `display ap all` 能看到 AP 注册为 `nor`，`display radio all` 四个 radio 都是 `on`。
- 但 `display vap ssid all` 恒为 `Total: 0`，AP 侧 `display current-configuration | include vap` 为空。
- STA 无法关联，`display station all` 为 0。

## 复现环境

- eNSP 1.2.00.510，AC6005（VRP 5.160），AP6050DN ×2，S5700 接入。
- 已试 4 种配置：`ap-group default` 绑定 `radio all`、去掉 `radio all`、service-vlan 100→30、
  尝试 `undo forward-mode`（该镜像不支持）。

## 结论

本机 AC6005 镜像不实例化 VAP，属镜像/环境限制，不是配置遗漏。
历史归档中另一台机器的同型号实验成功（SSID ON、STA 取址），说明与镜像/宿主环境有关。

## 规避

- 漫游类验证改用物理 AC/AP，或更换 AC 镜像版本。
- 拓扑生成时不要把"WLAN 漫游通过"当作已验证事实。

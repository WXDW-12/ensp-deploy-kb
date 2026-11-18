# Cloud 需要 Npcap 兼容模式

## 现象

- eNSP Cloud 设备无法启动/端口不显示。
- `Npcap` 安装时未勾选 `WinPcap API-compatible Mode`。

## 检查

```
reg query HKLM\SOFTWARE\WOW6432Node\Npcap /v WinPcapCompatible
```

值为 0 时 Cloud 不可用。

## 解决

重装 Npcap，勾选 WinPcap 兼容模式，重启后再启动 Cloud。

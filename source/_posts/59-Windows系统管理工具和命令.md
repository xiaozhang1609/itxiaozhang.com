---
title: Windows系统管理工具和命令
permalink: /windows-system-management-tools-and-commands/
date: 2024-01-01 15:42:06
categories: 
  - 电脑维修
tags: 
  - 电脑维修
  - cmd
---

### 管理工具

- **设备管理器** (`devmgmt.msc`)：管理硬件设备、安装驱动及排查硬件故障。

- **程序和功能** (`appwiz.cpl`)：卸载或修改已安装程序。

- **计算机管理** (`compmgmt.msc`)：集成了多项管理工具，如事件查看器与磁盘管理。

- **控制面板** (`control`)：提供多样化的系统设置与管理选项。

- **资源管理器** (`explorer`)：用于文件与文件夹管理，全面访问系统资源。

### 诊断与优化命令

- **DirectX信息检查** (`dxdiag`)：展示DirectX配置详情。

- **Windows防火墙** (`firewall.cpl`)：管理网络流量，确保系统安全。

- **系统文件检查器** (`sfc /scannow`)：扫描并修复系统文件问题。

- **DISM 工具**：通过命令如 `DISM /Online /Cleanup-Image` 维护Windows映像。

### 网络管理命令

- **网络适配器** (`ncpa.cpl`)：管理网络连接。

- **磁盘管理** (`diskmgmt.msc`)：硬盘分区与驱动器管理。

- **跟踪路由** (`tracert IP/域名`)：诊断网络路径与连接问题。

### 用户账户管理

- **新增用户** (`control userpasswords2`)：账户添加与修改。

- **禁用管理员账户** (`net user administrator /active:no`)：禁用默认管理员权限。

### 其他常见命令

- **ipconfig**：查看与管理IP配置。

- **netstat**：显示活动网络连接及端口。

- **ping**：测试网络连接，确认目标可达性。

- **nslookup**：查询DNS信息。

- **shutdown**：关机、重启或注销系统。

- **tasklist**：列出当前运行进程。

- **taskkill**：终止指定进程。

- **regedit**：访问Windows注册表编辑器。

- **chkdsk**：检测与修复磁盘错误。

- **diskpart**：高级磁盘分区管理。

- **本地安全策略** (`secpol.msc`)：配置本地安全设置。

- **系统配置实用程序** (`msconfig`)：调整启动项与服务。

- **Windows备份与恢复**：系统备份与还原操作。

- **资源监视器** (`resmon`)：监控系统性能与资源使用。

- **计划任务** (`taskschd.msc`)：安排自动执行的任务。

- **远程桌面连接** (`mstsc`)：实现远程计算机访问。

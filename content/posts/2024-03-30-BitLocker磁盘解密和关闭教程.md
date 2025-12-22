---
title: BitLocker磁盘解密和关闭教程
url: /bitlocker-key-recovery-deactivation/
date: '2024-03-30 21:09:01 +0800'
description: 
categories:
  - 电脑维修
tags:
  - windows
  - win10
  - win11
  - bitlocker
  - 电脑维修
author: IT小章
---
## 1. 什么是BitLocker？

**BitLocker** 是微软推出的一个磁盘分区加密方案。它首次出现在 Windows Vista 中，是一种数据保护功能，主要用于防止因计算机设备丢失而导致的数据泄露或被窃。一旦加密，若无密钥，即使是微软本身也无法破解，因此它提供了强大的数据安全保护。但同时，如果忘记或丢失密钥，可能会导致数据无法访问。

<!--more-->

## 2. 判断磁盘是否被BitLocker加密

打开“我的电脑”，检查磁盘驱动器图标是否有“锁”标志，以此来判断磁盘是否已被BitLocker加密。

## 3. 找回BitLocker密钥

### 3.1 能进入Windows系统

1. 右键单击已加密的磁盘，选择“管理BitLocker”。
2. 点击“备份恢复密钥”。
3. 根据需求选择保存到Microsoft账户、保存到文件或打印恢复密钥。

### 3.2 不能进入Windows系统

#### 方法1: 登录Microsoft账户

（前提是使用Microsoft账户登录过Windows）

1. 访问 <https://account.microsoft.com> 并登录账户。
2. 单击这个[地址](https://account.microsoft.com/devices/recoverykey)可以直达，如果不行的话，看下面的步骤。
3. 点击“查看所有设备”，找到被锁定的电脑。
4. 点击电脑的“信息和支持”。
5. 点击“管理恢复密钥”。
6. 输入密码，查看并保存BitLocker密钥。

#### 方法2: 从U盘恢复

（前提是已将密钥备份到U盘）

1. 插入U盘，点击“我忘记了密码”。
2. 选择“键入恢复密钥”。
3. 打开U盘中的密钥文件，复制最后一行数字。
4. 输入该数字作为BitLocker恢复密钥。

## 4. Windows 10 关闭 BitLocker  

1. 右键单击要解密的磁盘，选择“管理BitLocker”。
2. 点击“关闭BitLocker”。
3. 确认提示后，等待解密完成。

## 5. Windows 11 关闭 BitLocker

1. 搜索并打开“设备加密设置”。
2. 将“设备加密”选项设为“关闭”。
3. 确认提示后，等待解密完成。

## 6. 注意事项

- 解密时间取决于文件数量，请耐心等待。
- 解密过程中不要断电或关机，以免造成数据损坏。
- 定期备份重要数据，以防数据丢失。
- 如果没有重要数据，可以考虑关闭BitLocker，以避免将来忘记密钥的问题。

---
title: MSI文件安装失败
permalink: /msi-installation-failure/
date: 2024-01-01 15:42:06
categories: 
  - 电脑维修
tags: 
  - win10
  - win11
  - windows
  - 电脑维修
---

**解决Windows 10安装MSI程序的异常问题：使用MSIEXEC命令进行安装**

<!--more-->
* * *

**异常信息：**  
在安装MSI程序包时遇到以下错误信息：

- "The installer has encountered an unexpected error installing this package. This may indicate a problem with this package. The error code is 2503."

- "The installer has encountered an unexpected error installing this package. This may indicate a problem with this package. The error code is 2502."

这些错误通常表示Windows 10系统在安装带有`.msi`后缀的程序时权限不足。

**解决方法：**

1. **以管理员身份运行命令提示符（CMD）：**

- 在Windows搜索栏中输入“cmd”。

- 右键点击“命令提示符”，选择“以管理员身份运行”。

1. **进入MSI文件所在目录：**

- 使用`cd`命令进入MSI文件所在的文件夹。

1. **执行安装命令：**

- 输入命令`msiexec /package node-v10.14.2-x64.msi`，然后按回车。

- 也可以使用全路径的方式执行命令。

1. **按照提示完成安装：**

- 安装向导页面会自动弹出。

- 按照页面上的提示完成安装过程。

1. **验证安装是否成功：**

- 输入命令`node -v`。

- 如果看到版本号显示，表示安装成功。

_来源：[win10 安装msi程序异常解决，使用msiexec命令安装\_msiexec /package-CSDN博客](https://blog.csdn.net/axing2015/article/details/85283075)_

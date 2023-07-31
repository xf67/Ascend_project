# 升级固件

目前两张板卡的固件应该都是可以下载到的最新版本21.0.4。

**注意：升级固件可能会导致SSD损坏！**

**注意：升级固件可能会导致SSD损坏！**

**注意：升级固件可能会导致SSD损坏！**

## 升级流程

以Hw用户登录到板卡，再使用`su`命令到root用户。

下载驱动包A200dk-npu-driver-*{software version}*-ubuntu18.04-aarch64-minirc.tar.gz。

在`opt/mini`目录下执行`tar --no-same-owner -zxf A200dk-npu-driver-{software version}-ubuntu18.04-aarch64-minirc.tar.gz的路径 --strip-components 2 driver/scripts/minirc_install_phase1.sh`

然后执行`./minirc_install_phase1.sh`

接下来重启`reboot`

[参考华为文档](https://www.hiascend.com/document/detail/zh/Atlas200DKDeveloperKit/1013/environment/atlased_04_0024.html)